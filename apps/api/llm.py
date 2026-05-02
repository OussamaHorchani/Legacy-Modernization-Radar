import logging
import os
import re
import time
from collections import Counter
from pathlib import Path

import httpx
from dotenv import load_dotenv

from schema import Hotspot, ScanResult, Workstream

load_dotenv(Path(__file__).with_name(".env"))

logger = logging.getLogger("uvicorn.error")

DEFAULT_WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
DEFAULT_WATSONX_MODEL_ID = "ibm/granite-3-8b-instruct"
IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
IAM_GRANT_TYPE = "urn:ibm:params:oauth:grant-type:apikey"
BANNED_MODELS = {
    "llama-3-405b-instruct",
    "mistral-medium-2502",
    "mistral-small-3-1-24b-instruct-2503",
}

# Phrases the model loves but humans hate. We tell it explicitly to avoid these
# AND we run a post-hoc sanitizer that removes them or rephrases.
BANNED_PHRASES = [
    "engineering risk",
    "delivery risk",
    "concrete engineering",
    "modernization efforts",
    "modernization posture",
    "modernization tasks",
    "strategic alignment",
    "low-friction",
    "encumbrances",
    "posture for modernization",
    "subsequent modernization",
    "subsequent architectural",
    "risk-bearing",
    "this matters",
    "it is crucial",
    "in conclusion",
    "in summary",
    "leverage",
    "robust",
]
BANNED_LIST = ", ".join(f'"{phrase}"' for phrase in BANNED_PHRASES)

# Used after generation to strip any banned phrase the model still slipped in.
# Replacements aim to keep grammar intact rather than just deleting.
SANITIZE_REPLACEMENTS = [
    (r"\bmodernization posture\b", "state"),
    (r"\bposture\b", "state"),
    (r"\bmodernization efforts\b", "work"),
    (r"\bmodernization tasks\b", "work"),
    (r"\bsubsequent modernization\b", "follow-on work"),
    (r"\bsubsequent architectural\b", "follow-on"),
    (r"\bengineering risk\b", "exposure"),
    (r"\bdelivery risk\b", "schedule risk"),
    (r"\bconcrete engineering\b", "specific"),
    (r"\bstrategic alignment\b", "clear sequencing"),
    (r"\blow-friction\b", "straightforward"),
    (r"\bencumbrances\b", "blockers"),
    (r"\brisk-bearing\b", "risky"),
    (r"\bin conclusion,?\s*", ""),
    (r"\bin summary,?\s*", ""),
    (r"\bleverage\b", "use"),
    (r"\brobustness\b", "reliability"),
    (r"\brobustly\b", "reliably"),
    (r"\brobust\b", "reliable"),
    (r"\bit is crucial\b", "we should"),
]

_IAM_TOKEN: str | None = None
_IAM_TOKEN_EXPIRATION = 0.0
_CLIENT_INITIALIZED = False


class WatsonxUnavailable(RuntimeError):
    pass


def initialize_watsonx_client() -> None:
    global _CLIENT_INITIALIZED

    if _CLIENT_INITIALIZED:
        return

    _ = _get_config()
    logger.info("watsonx.ai client initialized")
    _CLIENT_INITIALIZED = True


def get_iam_token() -> str:
    global _IAM_TOKEN, _IAM_TOKEN_EXPIRATION

    if _IAM_TOKEN and time.time() < (_IAM_TOKEN_EXPIRATION - 300):
        return _IAM_TOKEN

    config = _get_config()

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                IAM_TOKEN_URL,
                data={
                    "grant_type": IAM_GRANT_TYPE,
                    "apikey": config["api_key"],
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
    except httpx.TimeoutException as exc:
        raise WatsonxUnavailable("watsonx IAM token request timed out") from exc
    except httpx.HTTPError as exc:
        raise WatsonxUnavailable("watsonx IAM token request failed") from exc

    if response.status_code != 200:
        raise WatsonxUnavailable(
            f"watsonx IAM token request failed with status {response.status_code}"
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise WatsonxUnavailable("watsonx IAM token response was not valid JSON") from exc

    access_token = payload.get("access_token")
    if not access_token:
        raise WatsonxUnavailable("watsonx IAM token response did not include a token")

    expiration = payload.get("expiration")
    expires_in = payload.get("expires_in")
    if expiration is not None:
        _IAM_TOKEN_EXPIRATION = float(expiration)
    elif expires_in is not None:
        _IAM_TOKEN_EXPIRATION = time.time() + float(expires_in)
    else:
        _IAM_TOKEN_EXPIRATION = time.time() + 3600

    _IAM_TOKEN = access_token
    return access_token


def generate_text(prompt: str, max_tokens: int = 300) -> str:
    config = _get_config()
    bearer_token = get_iam_token()
    min_new_tokens = min(30, max_tokens)

    body = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": max_tokens,
            "min_new_tokens": min_new_tokens,
            "stop_sequences": [],
            "repetition_penalty": 1.05,
        },
        "model_id": config["model_id"],
        "project_id": config["project_id"],
    }

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                f"{config['url']}/ml/v1/text/generation?version=2024-05-29",
                json=body,
                headers={
                    "Authorization": f"Bearer {bearer_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
    except httpx.TimeoutException as exc:
        raise WatsonxUnavailable("watsonx text generation timed out") from exc
    except httpx.HTTPError as exc:
        raise WatsonxUnavailable("watsonx text generation request failed") from exc

    if response.status_code != 200:
        raise WatsonxUnavailable(
            f"watsonx text generation failed with status {response.status_code}"
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise WatsonxUnavailable("watsonx text generation response was not valid JSON") from exc

    results = payload.get("results")
    if not isinstance(results, list) or not results:
        raise WatsonxUnavailable("watsonx text generation response did not include results")

    generated_text = results[0].get("generated_text")
    if not isinstance(generated_text, str) or not generated_text.strip():
        raise WatsonxUnavailable("watsonx text generation response was empty")

    return _sanitize(_normalize_generated_text(_extract_answer(generated_text)))


def build_hotspot_narrative_prompt(hotspot: Hotspot) -> str:
    affected_files = "\n".join(f"- {file}" for file in hotspot.affected_files) or "- none listed"
    return (
        "You are a senior staff engineer writing a one-paragraph note for a tech lead "
        "who has 15 seconds to read it. The reader already knows what the hotspot is — do NOT restate it. "
        "Tell them concretely what could go wrong in production or in the next sprint, "
        "and reference the actual code element by name when useful.\n\n"
        "Hard rules:\n"
        "1. Exactly 2 sentences. No more.\n"
        "2. Sentence 1 MUST start with the word 'A', 'An', 'Without', 'When', 'If', or 'Because'.\n"
        "3. Do NOT repeat the title.\n"
        "4. Do NOT use the word 'hotspot' or the phrase 'this hotspot'.\n"
        "5. Do NOT use any of these banned phrases: " + BANNED_LIST + ".\n"
        "6. Be specific. If it is a CVE, name the attack scenario. "
        "If it is a missing test, name what behavior could regress. "
        "If it is a complex method, name the consequence (perf, brittleness, debugging cost).\n"
        "7. Plain prose. No bullets, headings, lists, or quotes.\n"
        "8. Reply only inside <answer></answer> tags.\n\n"
        f"Code element: {hotspot.title}\n"
        f"Severity: {hotspot.severity}\n"
        f"Category: {hotspot.category}\n"
        f"Detector finding: {hotspot.summary}\n"
        f"Recommended action: {hotspot.recommended_action}\n"
        "Affected files:\n"
        f"{affected_files}\n\n"
        "<answer>"
    )


def build_executive_summary_prompt(scan_result: ScanResult) -> str:
    counts = Counter(hotspot.severity for hotspot in scan_result.hotspots)
    critical = counts.get("Critical", 0)
    high = counts.get("High", 0)
    medium = counts.get("Medium", 0)
    low = counts.get("Low", 0)
    total = len(scan_result.hotspots)
    score = scan_result.readiness_score

    if total == 0:
        # Clean repo prompt — different shape entirely.
        return (
            "You are writing a one-paragraph status note for an engineering leader. "
            "The Radar scanned this repository and found no flagged modernization issues. "
            "The readiness score is 100 out of 100.\n\n"
            "Hard rules:\n"
            "1. Exactly 2 sentences.\n"
            "2. Sentence 1: state plainly that the scanner found nothing flagged at this snapshot.\n"
            "3. Sentence 2: note that this reflects the current detector scope, not a guarantee of zero risk.\n"
            "4. Do NOT use the words 'posture', 'low-friction', 'encumbrances', or 'modernization posture'.\n"
            "5. Do NOT use any of these banned phrases: " + BANNED_LIST + ".\n"
            "6. Plain prose, professional, direct. No bullets, no headings, no quotes.\n"
            "7. Reply only inside <answer></answer> tags.\n\n"
            "<answer>"
        )

    # Has hotspots. Pick the most severe finding to anchor sentence 1.
    severity_order = ["Critical", "High", "Medium", "Low"]
    most_severe = next(
        (
            hotspot
            for level in severity_order
            for hotspot in scan_result.hotspots
            if hotspot.severity == level
        ),
        scan_result.hotspots[0],
    )

    severity_phrase = []
    if critical:
        severity_phrase.append(f"{critical} critical")
    if high:
        severity_phrase.append(f"{high} high")
    if medium:
        severity_phrase.append(f"{medium} medium")
    if low:
        severity_phrase.append(f"{low} low")
    severity_summary = ", ".join(severity_phrase)

    titles_block = "\n".join(
        f"- {h.severity}: {h.title}" for h in scan_result.hotspots
    )

    return (
        "You are writing the top-of-dashboard summary for an engineering leader. "
        "They want to know what the Radar found and what to do first.\n\n"
        "Hard rules:\n"
        "1. Exactly 3 sentences.\n"
        f"2. Sentence 1 MUST start with 'The repository scores {score}/100' and then name the most severe finding by title: {most_severe.title!r}.\n"
        "3. Sentence 2 MUST start with 'Address' and state which finding to fix first and one reason why.\n"
        "4. Sentence 3 MUST start with 'The remaining' and characterize the rest of the work as either deferrable or sequenced behind sentence 2.\n"
        "5. Do NOT use the word 'posture' anywhere.\n"
        "6. Do NOT use any of these banned phrases: " + BANNED_LIST + ".\n"
        "7. Plain prose, professional, direct. No bullets, no headings, no quotes.\n"
        "8. Reply only inside <answer></answer> tags.\n\n"
        f"Readiness score: {score}/100\n"
        f"Hotspot counts: {severity_summary}\n"
        f"Total hotspots: {total}\n"
        f"Most severe finding: {most_severe.title}\n"
        "All hotspots:\n"
        f"{titles_block}\n\n"
        "<answer>"
    )


def build_workstream_rationale_prompt(
    workstream: Workstream, hotspots: list[Hotspot]
) -> str:
    hotspot_lines = "\n".join(
        f"- {hotspot.severity} | {hotspot.title}"
        for hotspot in hotspots
    )

    phase_intent = {
        "now": "These are immediate blockers — security or runtime risks that must land first.",
        "next": "These are stabilization items — fix after blockers but before broader work.",
        "later": "These are quality and cleanup items — safe to defer until higher-risk work is done.",
    }.get(workstream.phase, "")

    starter_rule = {
        "now": "Sentence MUST start with 'Fix first'.",
        "next": "Sentence MUST start with 'Stabilize'.",
        "later": "Sentence MUST start with 'Defer'.",
    }.get(workstream.phase, "Sentence MUST be a direct statement.")

    return (
        "You are writing one short rationale sentence for a roadmap column header.\n\n"
        "Hard rules:\n"
        "1. Exactly one sentence, under 22 words.\n"
        f"2. {starter_rule}\n"
        "3. Do NOT restate hotspot titles verbatim.\n"
        "4. Do NOT use any of these banned phrases: " + BANNED_LIST + ".\n"
        "5. Do NOT use the words 'posture', 'subsequent', or 'modernization' anywhere.\n"
        "6. Plain prose. No bullets, no quotes, no headings.\n"
        "7. Reply only inside <answer></answer> tags.\n\n"
        f"Phase: {workstream.phase}\n"
        f"Phase intent: {phase_intent}\n"
        "Hotspots in this phase:\n"
        f"{hotspot_lines}\n\n"
        "<answer>"
    )


def enrich_with_narratives(scan_result: ScanResult) -> None:
    initialize_watsonx_client()

    scan_result.executive_summary = _limit_sentences(
        generate_text(
            build_executive_summary_prompt(scan_result),
            max_tokens=170,
        ),
        3,
    )

    for hotspot in scan_result.hotspots:
        hotspot.narrative = _limit_sentences(
            generate_text(
                build_hotspot_narrative_prompt(hotspot),
                max_tokens=110,
            ),
            2,
        )

    hotspot_lookup = {hotspot.id: hotspot for hotspot in scan_result.hotspots}
    for workstream in scan_result.workstreams:
        grouped_hotspots = [
            hotspot_lookup[hotspot_id]
            for hotspot_id in workstream.hotspot_ids
            if hotspot_id in hotspot_lookup
        ]
        workstream.rationale = _limit_sentences(
            generate_text(
                build_workstream_rationale_prompt(workstream, grouped_hotspots),
                max_tokens=60,
            ),
            1,
        )


def _get_config() -> dict[str, str]:
    api_key = os.getenv("WATSONX_API_KEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    url = os.getenv("WATSONX_URL", DEFAULT_WATSONX_URL).rstrip("/")
    model_id = os.getenv("WATSONX_MODEL_ID", DEFAULT_WATSONX_MODEL_ID)

    if not api_key or not project_id:
        raise WatsonxUnavailable("watsonx configuration is incomplete")
    if model_id in BANNED_MODELS:
        raise WatsonxUnavailable("watsonx configured model is not permitted")

    return {
        "api_key": api_key,
        "project_id": project_id,
        "url": url,
        "model_id": model_id,
    }


def _normalize_generated_text(value: str) -> str:
    return " ".join(value.strip().split())


def _extract_answer(value: str) -> str:
    start_tag = "<answer>"
    # Tolerate broken end tags like "</answer" (no closing bracket) or "</answer ".
    end_tag_pattern = re.compile(r"</\s*answer\s*>?", re.IGNORECASE)

    start = value.find(start_tag)
    end_match = end_tag_pattern.search(value)
    end = end_match.start() if end_match else -1

    if start != -1 and end != -1 and end > start:
        value = value[start + len(start_tag):end]
    elif end != -1:
        # Model emitted only a closing tag (because we pre-seeded <answer>).
        value = value[:end]
    elif start != -1:
        # Open tag with no close — take everything after the open.
        value = value[start + len(start_tag):]

    # Belt and braces: strip any residual tag remnants.
    value = end_tag_pattern.sub(" ", value)
    value = value.replace(start_tag, " ")
    value = value.replace("```", " ")
    return value


def _sanitize(value: str) -> str:
    """Post-hoc replace banned phrases with neutral alternatives."""
    sanitized = value
    for pattern, replacement in SANITIZE_REPLACEMENTS:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    # Collapse any double spaces from substitutions.
    sanitized = re.sub(r"\s{2,}", " ", sanitized).strip()
    return sanitized


def _limit_sentences(value: str, count: int) -> str:
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", value)
        if sentence.strip()
    ]
    if not sentences:
        return value.strip()
    return " ".join(sentences[:count]).strip()
