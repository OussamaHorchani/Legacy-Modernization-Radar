import logging
from pathlib import Path

from llm import WatsonxUnavailable, enrich_with_narratives
from schema import Hotspot, ScanResult, Workstream

from scanners import sort_hotspots
from scanners.clone import CloneError, shallow_clone
from scanners.complex_methods import scan_complex_methods
from scanners.dependency_cve import scan_dependencies
from scanners.test_coverage import scan_test_coverage

SEVERITY_TO_PHASE = {
    "Critical": "now",
    "High": "next",
    "Medium": "later",
    "Low": "later",
}

WORKSTREAM_TEMPLATES = {
    "Critical": (
        "0.5-1 day",
        "Removes the most urgent runtime or supply-chain risk before broader rollout.",
    ),
    "High": (
        "1-2 days",
        "Stabilizes a risky implementation path before deeper modernization changes.",
    ),
    "Medium": (
        "0.5-1 day",
        "Backfills quality guardrails to reduce regression risk during follow-on work.",
    ),
    "Low": (
        "0.5 day",
        "Cleans up lower-severity issues that can be folded into later hardening work.",
    ),
}

SEVERITY_PENALTIES = {
    "Critical": 25,
    "High": 15,
    "Medium": 5,
    "Low": 1,
}

logger = logging.getLogger("uvicorn.error")


def run_scan(repo_url: str, branch: str) -> ScanResult:
    try:
        with shallow_clone(repo_url, branch) as repo_path:
            hotspots = _run_detectors(repo_path)
    except CloneError:
        return ScanResult(
            scan_id="",
            repo_url=repo_url,
            branch=branch,
            readiness_score=0,
            hotspots=[],
            workstreams=[],
        )
    except Exception:
        return ScanResult(
            scan_id="",
            repo_url=repo_url,
            branch=branch,
            readiness_score=0,
            hotspots=[],
            workstreams=[],
        )

    ordered_hotspots = sort_hotspots(_dedupe_hotspots(hotspots))
    result = ScanResult(
        scan_id="",
        repo_url=repo_url,
        branch=branch,
        readiness_score=calculate_readiness(ordered_hotspots) if ordered_hotspots else 100,
        hotspots=ordered_hotspots,
        workstreams=group_into_workstreams(ordered_hotspots),
    )

    try:
        enrich_with_narratives(result)
    except WatsonxUnavailable as exc:
        logger.warning(
            "watsonx.ai unavailable, returning deterministic result",
            extra={"reason": str(exc)},
        )

    return result


def calculate_readiness(hotspots: list[Hotspot]) -> int:
    score = 100
    for hotspot in hotspots:
        score -= SEVERITY_PENALTIES[hotspot.severity]
    return max(score, 0)


def group_into_workstreams(hotspots: list[Hotspot]) -> list[Workstream]:
    grouped: dict[str, list[Hotspot]] = {"now": [], "next": [], "later": []}
    for hotspot in hotspots:
        grouped[SEVERITY_TO_PHASE[hotspot.severity]].append(hotspot)

    workstreams: list[Workstream] = []
    for phase in ("now", "next", "later"):
        phase_hotspots = grouped[phase]
        if not phase_hotspots:
            continue

        template = WORKSTREAM_TEMPLATES[phase_hotspots[0].severity]
        workstreams.append(
            Workstream(
                phase=phase,
                hotspot_ids=[hotspot.id for hotspot in phase_hotspots],
                effort=template[0],
                impact=template[1],
            )
        )

    return workstreams


def _run_detectors(repo_path: Path) -> list[Hotspot]:
    hotspots: list[Hotspot] = []
    for detector in (scan_dependencies, scan_test_coverage, scan_complex_methods):
        try:
            hotspots.extend(detector(repo_path))
        except Exception:
            continue
    return hotspots


def _dedupe_hotspots(hotspots: list[Hotspot]) -> list[Hotspot]:
    unique: dict[str, Hotspot] = {}
    for hotspot in hotspots:
        unique[hotspot.id] = hotspot
    return list(unique.values())
