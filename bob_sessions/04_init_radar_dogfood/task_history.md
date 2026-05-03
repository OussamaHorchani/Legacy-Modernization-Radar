**User:**

<task>
I'm working on the Legacy Modernization Radar — a control-tower web app that scans legacy repositories, ranks modernization hotspots, and hands one approved fix to IBM Bob. I need a comprehensive AGENTS.md file at the repo root that captures:

Project overview — what this app does, who it's for, and the key user flow (paste repo URL → see scan results → click hotspot → preview the Bob handoff pack).
Architecture — the monorepo layout (apps/api FastAPI Python 3.11, apps/web Vite + React + TypeScript + Tailwind), how the two halves communicate, and the key modules. Specifically mention the scanner detector pipeline (apps/api/scanners/), the watsonx.ai narrative integration (apps/api/llm.py), the schema (apps/api/schema.py mirrored in apps/web/src/lib/types.ts), and the main UI component (apps/web/src/App.tsx).
Key design decisions — why deterministic detectors are the source of truth and watsonx.ai is additive (with a WatsonxUnavailable fallback so the demo never breaks), why we use forced-sentence-starter prompts plus a post-hoc sanitizer for IBM Granite, why scan results are cached in-memory keyed by scan_id, and why the frontend polls instead of using websockets.
Build and run — local dev (uvicorn for API, npm run dev for web), docker-compose for full-stack local, Fly.io deploy for API (apps/api/fly.toml), and Vercel for web (apps/web/.env.production has VITE_API_URL).
Configuration surface — every environment variable read by the app: WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL, WATSONX_MODEL_ID, PORT, CORS_ORIGINS, VITE_API_URL. Note which are secrets vs public, and where they're set in dev vs production. Mention that apps/api/.env is gitignored and never committed.
Test surface — what's currently tested, what isn't, and the specific gaps Bob would prioritize first if asked to add coverage.
Notable conventions — TypeScript types in apps/web/src/lib/types.ts mirror Pydantic models in apps/api/schema.py and are kept in sync manually; production-ready Dockerfiles for both apps; .env files are gitignored.

Write the file to ./AGENTS.md. Be specific and concrete. Reference actual file paths and module names. Avoid generic advice.
</task>
<environment_details>
# VSCode Visible Files


# VSCode Open Tabs


# Current Time
Current time in ISO 8601 UTC format: 2026-05-03T01:16:04.679Z
User time zone: Africa/Tunis, UTC+1:00

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>


# Current Workspace Directory (/Users/oussama/dev/hackathon/Legacy-Modernization-Radar) Files
.gitignore
docker-compose.yml
README.md
apps/
apps/api/
apps/api/.dockerignore
apps/api/Dockerfile
apps/api/fly.toml
apps/api/llm.py
apps/api/main.py
apps/api/pyproject.toml
apps/api/schema.py
apps/api/scanners/
apps/api/scanners/__init__.py
apps/api/scanners/clone.py
apps/api/scanners/complex_methods.py
apps/api/scanners/dependency_cve.py
apps/api/scanners/runner.py
apps/api/scanners/test_coverage.py
apps/web/
apps/web/.env.production
apps/web/.gitignore
apps/web/Dockerfile
apps/web/eslint.config.js
apps/web/index.html
apps/web/nginx.conf
apps/web/package-lock.json
apps/web/package.json
apps/web/postcss.config.js
apps/web/tsconfig.app.json
apps/web/tsconfig.json
apps/web/tsconfig.node.json
apps/web/vite.config.ts
apps/web/.vercel/
apps/web/src/
apps/web/src/App.tsx
apps/web/src/index.css
apps/web/src/main.tsx
apps/web/src/lib/
apps/web/src/lib/types.ts
bob_sessions/
bob_sessions/01_init_petclinic_baseline/
bob_sessions/01_init_petclinic_baseline/AGENTS.md
bob_sessions/01_init_petclinic_baseline/consumption_summary.png
bob_sessions/01_init_petclinic_baseline/task_history.md
bob_sessions/02_modernization_analysis/
bob_sessions/02_modernization_analysis/consumption_summary.png
bob_sessions/02_modernization_analysis/MODERNIZATION_ANALYSIS.md
bob_sessions/02_modernization_analysis/task_history.md
bob_sessions/03_hero_patch_cve/
bob_sessions/03_hero_patch_cve/after_patch_dashboard.png
bob_sessions/03_hero_patch_cve/before_patch_dashboard.png
bob_sessions/03_hero_patch_cve/consumption_summary.png
bob_sessions/03_hero_patch_cve/RECORDING.md
bob_sessions/03_hero_patch_cve/task_history.md
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll gather information about the project structure and implementation details to create a comprehensive AGENTS.md file.

<read_file>
<args>
  <file>
    <path>README.md</path>
  </file>
  <file>
    <path>apps/api/main.py</path>
  </file>
  <file>
    <path>apps/api/schema.py</path>
  </file>
  <file>
    <path>apps/api/llm.py</path>
  </file>
  <file>
    <path>apps/web/src/lib/types.ts</path>
  </file>
</args>
</read_file>

---

**User:**

[read_file for 5 files] Result:
<files>
<file><path>README.md</path>
<content lines="1-49">
 1 | # Legacy Modernization Radar
 2 | 
 3 | Built for the IBM Bob Dev Day Hackathon, May 1-3, 2026.
 4 | 
 5 | A control-tower web app that scans legacy codebases, ranks modernization hotspots, and hands one approved fix to IBM Bob to execute with passing tests.
 6 | 
 7 | ## Local development
 8 | 
 9 | ### Docker Compose
10 | 
11 | From the repo root, build and run both services:
12 | 
13 | ```bash
14 | docker compose up --build
15 | ```
16 | 
17 | - Web UI: `http://localhost:8081`
18 | - API: `http://localhost:8080`
19 | - Health check: `curl http://localhost:8080/health`
20 | 
21 | The web build bakes `VITE_API_URL=http://localhost:8080`, so the browser talks to the API on port `8080` while the UI is served on port `8081`.
22 | 
23 | ### Native development
24 | 
25 | API terminal:
26 | 
27 | ```bash
28 | cd apps/api
29 | python3.11 -m venv .venv
30 | source .venv/bin/activate
31 | pip install -e .
32 | uvicorn main:app --port 8080
33 | ```
34 | 
35 | Web terminal:
36 | 
37 | ```bash
38 | cd apps/web
39 | npm install
40 | npm run dev
41 | ```
42 | 
43 | Ports:
44 | 
45 | - Vite dev server: `http://localhost:5173`
46 | - FastAPI: `http://localhost:8080`
47 | - Health check: `http://localhost:8080/health`
48 | 
49 | If you need to point the web app at a different backend, start Vite with `VITE_API_URL=http://localhost:8080 npm run dev`.
</content>
</file>
<file><path>apps/api/main.py</path>
<content lines="1-147">
  1 | import logging
  2 | import os
  3 | from contextlib import asynccontextmanager
  4 | from pathlib import Path
  5 | from uuid import uuid4
  6 | 
  7 | import uvicorn
  8 | from dotenv import load_dotenv
  9 | from fastapi import FastAPI, HTTPException
 10 | from fastapi.middleware.cors import CORSMiddleware
 11 | 
 12 | from llm import WatsonxUnavailable, generate_text, initialize_watsonx_client
 13 | from scanners.runner import run_scan
 14 | from schema import (
 15 |     ApproveResponse,
 16 |     HandoffPack,
 17 |     Hotspot,
 18 |     ScanCreateRequest,
 19 |     ScanCreateResponse,
 20 |     ScanResult,
 21 | )
 22 | 
 23 | load_dotenv(Path(__file__).with_name(".env"))
 24 | 
 25 | logger = logging.getLogger("uvicorn.error")
 26 | PORT = int(os.getenv("PORT", "8080"))
 27 | CORS_ORIGINS = [
 28 |     origin.strip()
 29 |     for origin in os.getenv("CORS_ORIGINS", "*").split(",")
 30 |     if origin.strip()
 31 | ]
 32 | SCAN_RESULTS: dict[str, ScanResult] = {}
 33 | 
 34 | 
 35 | def build_handoff_pack(hotspot_id: str) -> HandoffPack:
 36 |     hotspot = find_hotspot(hotspot_id)
 37 |     if hotspot is None:
 38 |         raise HTTPException(status_code=404, detail="Hotspot not found")
 39 | 
 40 |     return HandoffPack(
 41 |         hotspot_id=hotspot.id,
 42 |         title=f"Remediate {hotspot.title}",
 43 |         prompt=(
 44 |             f"Address the hotspot titled '{hotspot.title}'. {hotspot.summary} "
 45 |             f"Recommended action: {hotspot.recommended_action}"
 46 |         ),
 47 |         target_files=hotspot.affected_files,
 48 |         acceptance_criteria=[
 49 |             "The hotspot is no longer reported by the detector after the change.",
 50 |             "The relevant production behavior remains intact after remediation.",
 51 |             "The fix is documented clearly enough for a follow-on reviewer to validate quickly.",
 52 |         ],
 53 |         test_plan=[
 54 |             "Run the smallest focused test slice that exercises the affected area.",
 55 |             "Run at least one broader regression check for the surrounding module.",
 56 |             "Re-run the Radar scan and confirm this hotspot disappears or changes severity appropriately.",
 57 |         ],
 58 |     )
 59 | 
 60 | 
 61 | def find_hotspot(hotspot_id: str) -> Hotspot | None:
 62 |     for scan_result in SCAN_RESULTS.values():
 63 |         for hotspot in scan_result.hotspots:
 64 |             if hotspot.id == hotspot_id:
 65 |                 return hotspot
 66 |     return None
 67 | 
 68 | 
 69 | @asynccontextmanager
 70 | async def lifespan(_: FastAPI):
 71 |     print("Legacy Modernization Radar API starting up")
 72 |     try:
 73 |         initialize_watsonx_client()
 74 |     except WatsonxUnavailable as exc:
 75 |         logger.warning(
 76 |             "watsonx.ai client unavailable during startup",
 77 |             extra={"reason": str(exc)},
 78 |         )
 79 |     yield
 80 |     print("Legacy Modernization Radar API shutting down gracefully")
 81 | 
 82 | 
 83 | app = FastAPI(title="Legacy Modernization Radar API", lifespan=lifespan)
 84 | 
 85 | app.add_middleware(
 86 |     CORSMiddleware,
 87 |     allow_origins=CORS_ORIGINS,
 88 |     allow_credentials=False,
 89 |     allow_methods=["*"],
 90 |     allow_headers=["*"],
 91 | )
 92 | 
 93 | 
 94 | @app.get("/health")
 95 | async def health_check() -> dict[str, bool]:
 96 |     return {"ok": True}
 97 | 
 98 | 
 99 | @app.get("/api/llm/health")
100 | def llm_health() -> dict[str, bool | str]:
101 |     try:
102 |         _ = generate_text("Say OK.", max_tokens=5)
103 |     except WatsonxUnavailable as exc:
104 |         return {
105 |             "watsonx_available": False,
106 |             "reason": str(exc),
107 |         }
108 | 
109 |     return {"watsonx_available": True}
110 | 
111 | 
112 | @app.post("/api/scans", response_model=ScanCreateResponse)
113 | async def create_scan(request: ScanCreateRequest) -> ScanCreateResponse:
114 |     scan_id = str(uuid4())
115 |     scan_result = run_scan(request.repo_url, request.branch).model_copy(
116 |         update={
117 |             "scan_id": scan_id,
118 |             "repo_url": request.repo_url,
119 |             "branch": request.branch,
120 |             "scenario_id": request.scenario_id,
121 |         }
122 |     )
123 |     SCAN_RESULTS[scan_id] = scan_result
124 |     return ScanCreateResponse(scan_id=scan_id, status="started")
125 | 
126 | 
127 | @app.get("/api/scans/{scan_id}", response_model=ScanResult)
128 | async def get_scan(scan_id: str) -> ScanResult:
129 |     result = SCAN_RESULTS.get(scan_id)
130 |     if result is None:
131 |         raise HTTPException(status_code=404, detail="Scan not found")
132 |     return result
133 | 
134 | 
135 | @app.post("/api/hotspots/{hotspot_id}/approve", response_model=ApproveResponse)
136 | async def approve_hotspot(hotspot_id: str) -> ApproveResponse:
137 |     _ = build_handoff_pack(hotspot_id)
138 |     return ApproveResponse(ok=True)
139 | 
140 | 
141 | @app.post("/api/hotspots/{hotspot_id}/handoff", response_model=HandoffPack)
142 | async def handoff_hotspot(hotspot_id: str) -> HandoffPack:
143 |     return build_handoff_pack(hotspot_id)
144 | 
145 | 
146 | if __name__ == "__main__":
147 |     uvicorn.run("main:app", host="0.0.0.0", port=PORT)
</content>
</file>
<file><path>apps/api/schema.py</path>
<content lines="1-65">
 1 | from typing import Literal
 2 | 
 3 | from pydantic import BaseModel, Field
 4 | 
 5 | Severity = Literal["Critical", "High", "Medium", "Low"]
 6 | Category = Literal["runtime", "architecture", "quality"]
 7 | Phase = Literal["now", "next", "later"]
 8 | ScanStatus = Literal["started", "completed"]
 9 | 
10 | 
11 | class Hotspot(BaseModel):
12 |     id: str
13 |     title: str
14 |     severity: Severity
15 |     category: Category
16 |     summary: str
17 |     affected_files: list[str] = Field(default_factory=list)
18 |     recommended_action: str
19 |     cve_id: str | None = None
20 |     cvss_score: float | None = None
21 |     narrative: str | None = None
22 | 
23 | 
24 | class Workstream(BaseModel):
25 |     phase: Phase
26 |     hotspot_ids: list[str] = Field(default_factory=list)
27 |     effort: str
28 |     impact: str
29 |     rationale: str | None = None
30 | 
31 | 
32 | class ScanCreateRequest(BaseModel):
33 |     repo_url: str
34 |     branch: str
35 |     scenario_id: str | None = None
36 | 
37 | 
38 | class ScanCreateResponse(BaseModel):
39 |     scan_id: str
40 |     status: Literal["started"]
41 | 
42 | 
43 | class ScanResult(BaseModel):
44 |     scan_id: str
45 |     repo_url: str
46 |     branch: str
47 |     scenario_id: str | None = None
48 |     status: Literal["completed"] = "completed"
49 |     readiness_score: int
50 |     hotspots: list[Hotspot] = Field(default_factory=list)
51 |     workstreams: list[Workstream] = Field(default_factory=list)
52 |     executive_summary: str | None = None
53 | 
54 | 
55 | class ApproveResponse(BaseModel):
56 |     ok: bool = True
57 | 
58 | 
59 | class HandoffPack(BaseModel):
60 |     hotspot_id: str
61 |     title: str
62 |     prompt: str
63 |     target_files: list[str] = Field(default_factory=list)
64 |     acceptance_criteria: list[str] = Field(default_factory=list)
65 |     test_plan: list[str] = Field(default_factory=list)
</content>
</file>
<file><path>apps/api/llm.py</path>
<content lines="1-449">
  1 | import logging
  2 | import os
  3 | import re
  4 | import time
  5 | from collections import Counter
  6 | from pathlib import Path
  7 | 
  8 | import httpx
  9 | from dotenv import load_dotenv
 10 | 
 11 | from schema import Hotspot, ScanResult, Workstream
 12 | 
 13 | load_dotenv(Path(__file__).with_name(".env"))
 14 | 
 15 | logger = logging.getLogger("uvicorn.error")
 16 | 
 17 | DEFAULT_WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
 18 | DEFAULT_WATSONX_MODEL_ID = "ibm/granite-3-8b-instruct"
 19 | IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
 20 | IAM_GRANT_TYPE = "urn:ibm:params:oauth:grant-type:apikey"
 21 | BANNED_MODELS = {
 22 |     "llama-3-405b-instruct",
 23 |     "mistral-medium-2502",
 24 |     "mistral-small-3-1-24b-instruct-2503",
 25 | }
 26 | 
 27 | # Phrases the model loves but humans hate. We tell it explicitly to avoid these
 28 | # AND we run a post-hoc sanitizer that removes them or rephrases.
 29 | BANNED_PHRASES = [
 30 |     "engineering risk",
 31 |     "delivery risk",
 32 |     "concrete engineering",
 33 |     "modernization efforts",
 34 |     "modernization posture",
 35 |     "modernization tasks",
 36 |     "strategic alignment",
 37 |     "low-friction",
 38 |     "encumbrances",
 39 |     "posture for modernization",
 40 |     "subsequent modernization",
 41 |     "subsequent architectural",
 42 |     "risk-bearing",
 43 |     "this matters",
 44 |     "it is crucial",
 45 |     "in conclusion",
 46 |     "in summary",
 47 |     "leverage",
 48 |     "robust",
 49 | ]
 50 | BANNED_LIST = ", ".join(f'"{phrase}"' for phrase in BANNED_PHRASES)
 51 | 
 52 | # Used after generation to strip any banned phrase the model still slipped in.
 53 | # Replacements aim to keep grammar intact rather than just deleting.
 54 | SANITIZE_REPLACEMENTS = [
 55 |     (r"\bmodernization posture\b", "state"),
 56 |     (r"\bposture\b", "state"),
 57 |     (r"\bmodernization efforts\b", "work"),
 58 |     (r"\bmodernization tasks\b", "work"),
 59 |     (r"\bsubsequent modernization\b", "follow-on work"),
 60 |     (r"\bsubsequent architectural\b", "follow-on"),
 61 |     (r"\bengineering risk\b", "exposure"),
 62 |     (r"\bdelivery risk\b", "schedule risk"),
 63 |     (r"\bconcrete engineering\b", "specific"),
 64 |     (r"\bstrategic alignment\b", "clear sequencing"),
 65 |     (r"\blow-friction\b", "straightforward"),
 66 |     (r"\bencumbrances\b", "blockers"),
 67 |     (r"\brisk-bearing\b", "risky"),
 68 |     (r"\bin conclusion,?\s*", ""),
 69 |     (r"\bin summary,?\s*", ""),
 70 |     (r"\bleverage\b", "use"),
 71 |     (r"\brobustness\b", "reliability"),
 72 |     (r"\brobustly\b", "reliably"),
 73 |     (r"\brobust\b", "reliable"),
 74 |     (r"\bit is crucial\b", "we should"),
 75 | ]
 76 | 
 77 | _IAM_TOKEN: str | None = None
 78 | _IAM_TOKEN_EXPIRATION = 0.0
 79 | _CLIENT_INITIALIZED = False
 80 | 
 81 | 
 82 | class WatsonxUnavailable(RuntimeError):
 83 |     pass
 84 | 
 85 | 
 86 | def initialize_watsonx_client() -> None:
 87 |     global _CLIENT_INITIALIZED
 88 | 
 89 |     if _CLIENT_INITIALIZED:
 90 |         return
 91 | 
 92 |     _ = _get_config()
 93 |     logger.info("watsonx.ai client initialized")
 94 |     _CLIENT_INITIALIZED = True
 95 | 
 96 | 
 97 | def get_iam_token() -> str:
 98 |     global _IAM_TOKEN, _IAM_TOKEN_EXPIRATION
 99 | 
100 |     if _IAM_TOKEN and time.time() < (_IAM_TOKEN_EXPIRATION - 300):
101 |         return _IAM_TOKEN
102 | 
103 |     config = _get_config()
104 | 
105 |     try:
106 |         with httpx.Client(timeout=20.0) as client:
107 |             response = client.post(
108 |                 IAM_TOKEN_URL,
109 |                 data={
110 |                     "grant_type": IAM_GRANT_TYPE,
111 |                     "apikey": config["api_key"],
112 |                 },
113 |                 headers={
114 |                     "Content-Type": "application/x-www-form-urlencoded",
115 |                     "Accept": "application/json",
116 |                 },
117 |             )
118 |     except httpx.TimeoutException as exc:
119 |         raise WatsonxUnavailable("watsonx IAM token request timed out") from exc
120 |     except httpx.HTTPError as exc:
121 |         raise WatsonxUnavailable("watsonx IAM token request failed") from exc
122 | 
123 |     if response.status_code != 200:
124 |         raise WatsonxUnavailable(
125 |             f"watsonx IAM token request failed with status {response.status_code}"
126 |         )
127 | 
128 |     try:
129 |         payload = response.json()
130 |     except ValueError as exc:
131 |         raise WatsonxUnavailable("watsonx IAM token response was not valid JSON") from exc
132 | 
133 |     access_token = payload.get("access_token")
134 |     if not access_token:
135 |         raise WatsonxUnavailable("watsonx IAM token response did not include a token")
136 | 
137 |     expiration = payload.get("expiration")
138 |     expires_in = payload.get("expires_in")
139 |     if expiration is not None:
140 |         _IAM_TOKEN_EXPIRATION = float(expiration)
141 |     elif expires_in is not None:
142 |         _IAM_TOKEN_EXPIRATION = time.time() + float(expires_in)
143 |     else:
144 |         _IAM_TOKEN_EXPIRATION = time.time() + 3600
145 | 
146 |     _IAM_TOKEN = access_token
147 |     return access_token
148 | 
149 | 
150 | def generate_text(prompt: str, max_tokens: int = 300) -> str:
151 |     config = _get_config()
152 |     bearer_token = get_iam_token()
153 |     min_new_tokens = min(30, max_tokens)
154 | 
155 |     body = {
156 |         "input": prompt,
157 |         "parameters": {
158 |             "decoding_method": "greedy",
159 |             "max_new_tokens": max_tokens,
160 |             "min_new_tokens": min_new_tokens,
161 |             "stop_sequences": [],
162 |             "repetition_penalty": 1.05,
163 |         },
164 |         "model_id": config["model_id"],
165 |         "project_id": config["project_id"],
166 |     }
167 | 
168 |     try:
169 |         with httpx.Client(timeout=20.0) as client:
170 |             response = client.post(
171 |                 f"{config['url']}/ml/v1/text/generation?version=2024-05-29",
172 |                 json=body,
173 |                 headers={
174 |                     "Authorization": f"Bearer {bearer_token}",
175 |                     "Content-Type": "application/json",
176 |                     "Accept": "application/json",
177 |                 },
178 |             )
179 |     except httpx.TimeoutException as exc:
180 |         raise WatsonxUnavailable("watsonx text generation timed out") from exc
181 |     except httpx.HTTPError as exc:
182 |         raise WatsonxUnavailable("watsonx text generation request failed") from exc
183 | 
184 |     if response.status_code != 200:
185 |         raise WatsonxUnavailable(
186 |             f"watsonx text generation failed with status {response.status_code}"
187 |         )
188 | 
189 |     try:
190 |         payload = response.json()
191 |     except ValueError as exc:
192 |         raise WatsonxUnavailable("watsonx text generation response was not valid JSON") from exc
193 | 
194 |     results = payload.get("results")
195 |     if not isinstance(results, list) or not results:
196 |         raise WatsonxUnavailable("watsonx text generation response did not include results")
197 | 
198 |     generated_text = results[0].get("generated_text")
199 |     if not isinstance(generated_text, str) or not generated_text.strip():
200 |         raise WatsonxUnavailable("watsonx text generation response was empty")
201 | 
202 |     return _sanitize(_normalize_generated_text(_extract_answer(generated_text)))
203 | 
204 | 
205 | def build_hotspot_narrative_prompt(hotspot: Hotspot) -> str:
206 |     affected_files = "\n".join(f"- {file}" for file in hotspot.affected_files) or "- none listed"
207 |     return (
208 |         "You are a senior staff engineer writing a one-paragraph note for a tech lead "
209 |         "who has 15 seconds to read it. The reader already knows what the hotspot is — do NOT restate it. "
210 |         "Tell them concretely what could go wrong in production or in the next sprint, "
211 |         "and reference the actual code element by name when useful.\n\n"
212 |         "Hard rules:\n"
213 |         "1. Exactly 2 sentences. No more.\n"
214 |         "2. Sentence 1 MUST start with the word 'A', 'An', 'Without', 'When', 'If', or 'Because'.\n"
215 |         "3. Do NOT repeat the title.\n"
216 |         "4. Do NOT use the word 'hotspot' or the phrase 'this hotspot'.\n"
217 |         "5. Do NOT use any of these banned phrases: " + BANNED_LIST + ".\n"
218 |         "6. Be specific. If it is a CVE, name the attack scenario. "
219 |         "If it is a missing test, name what behavior could regress. "
220 |         "If it is a complex method, name the consequence (perf, brittleness, debugging cost).\n"
221 |         "7. Plain prose. No bullets, headings, lists, or quotes.\n"
222 |         "8. Reply only inside <answer></answer> tags.\n\n"
223 |         f"Code element: {hotspot.title}\n"
224 |         f"Severity: {hotspot.severity}\n"
225 |         f"Category: {hotspot.category}\n"
226 |         f"Detector finding: {hotspot.summary}\n"
227 |         f"Recommended action: {hotspot.recommended_action}\n"
228 |         "Affected files:\n"
229 |         f"{affected_files}\n\n"
230 |         "<answer>"
231 |     )
232 | 
233 | 
234 | def build_executive_summary_prompt(scan_result: ScanResult) -> str:
235 |     counts = Counter(hotspot.severity for hotspot in scan_result.hotspots)
236 |     critical = counts.get("Critical", 0)
237 |     high = counts.get("High", 0)
238 |     medium = counts.get("Medium", 0)
239 |     low = counts.get("Low", 0)
240 |     total = len(scan_result.hotspots)
241 |     score = scan_result.readiness_score
242 | 
243 |     if total == 0:
244 |         # Clean repo prompt — different shape entirely.
245 |         return (
246 |             "You are writing a one-paragraph status note for an engineering leader. "
247 |             "The Radar scanned this repository and found no flagged modernization issues. "
248 |             "The readiness score is 100 out of 100.\n\n"
249 |             "Hard rules:\n"
250 |             "1. Exactly 2 sentences.\n"
251 |             "2. Sentence 1: state plainly that the scanner found nothing flagged at this snapshot.\n"
252 |             "3. Sentence 2: note that this reflects the current detector scope, not a guarantee of zero risk.\n"
253 |             "4. Do NOT use the words 'posture', 'low-friction', 'encumbrances', or 'modernization posture'.\n"
254 |             "5. Do NOT use any of these banned phrases: " + BANNED_LIST + ".\n"
255 |             "6. Plain prose, professional, direct. No bullets, no headings, no quotes.\n"
256 |             "7. Reply only inside <answer></answer> tags.\n\n"
257 |             "<answer>"
258 |         )
259 | 
260 |     # Has hotspots. Pick the most severe finding to anchor sentence 1.
261 |     severity_order = ["Critical", "High", "Medium", "Low"]
262 |     most_severe = next(
263 |         (
264 |             hotspot
265 |             for level in severity_order
266 |             for hotspot in scan_result.hotspots
267 |             if hotspot.severity == level
268 |         ),
269 |         scan_result.hotspots[0],
270 |     )
271 | 
272 |     severity_phrase = []
273 |     if critical:
274 |         severity_phrase.append(f"{critical} critical")
275 |     if high:
276 |         severity_phrase.append(f"{high} high")
277 |     if medium:
278 |         severity_phrase.append(f"{medium} medium")
279 |     if low:
280 |         severity_phrase.append(f"{low} low")
281 |     severity_summary = ", ".join(severity_phrase)
282 | 
283 |     titles_block = "\n".join(
284 |         f"- {h.severity}: {h.title}" for h in scan_result.hotspots
285 |     )
286 | 
287 |     return (
288 |         "You are writing the top-of-dashboard summary for an engineering leader. "
289 |         "They want to know what the Radar found and what to do first.\n\n"
290 |         "Hard rules:\n"
291 |         "1. Exactly 3 sentences.\n"
292 |         f"2. Sentence 1 MUST start with 'The repository scores {score}/100' and then name the most severe finding by title: {most_severe.title!r}.\n"
293 |         "3. Sentence 2 MUST start with 'Address' and state which finding to fix first and one reason why.\n"
294 |         "4. Sentence 3 MUST start with 'The remaining' and characterize the rest of the work as either deferrable or sequenced behind sentence 2.\n"
295 |         "5. Do NOT use the word 'posture' anywhere.\n"
296 |         "6. Do NOT use any of these banned phrases: " + BANNED_LIST + ".\n"
297 |         "7. Plain prose, professional, direct. No bullets, no headings, no quotes.\n"
298 |         "8. Reply only inside <answer></answer> tags.\n\n"
299 |         f"Readiness score: {score}/100\n"
300 |         f"Hotspot counts: {severity_summary}\n"
301 |         f"Total hotspots: {total}\n"
302 |         f"Most severe finding: {most_severe.title}\n"
303 |         "All hotspots:\n"
304 |         f"{titles_block}\n\n"
305 |         "<answer>"
306 |     )
307 | 
308 | 
309 | def build_workstream_rationale_prompt(
310 |     workstream: Workstream, hotspots: list[Hotspot]
311 | ) -> str:
312 |     hotspot_lines = "\n".join(
313 |         f"- {hotspot.severity} | {hotspot.title}"
314 |         for hotspot in hotspots
315 |     )
316 | 
317 |     phase_intent = {
318 |         "now": "These are immediate blockers — security or runtime risks that must land first.",
319 |         "next": "These are stabilization items — fix after blockers but before broader work.",
320 |         "later": "These are quality and cleanup items — safe to defer until higher-risk work is done.",
321 |     }.get(workstream.phase, "")
322 | 
323 |     starter_rule = {
324 |         "now": "Sentence MUST start with 'Fix first'.",
325 |         "next": "Sentence MUST start with 'Stabilize'.",
326 |         "later": "Sentence MUST start with 'Defer'.",
327 |     }.get(workstream.phase, "Sentence MUST be a direct statement.")
328 | 
329 |     return (
330 |         "You are writing one short rationale sentence for a roadmap column header.\n\n"
331 |         "Hard rules:\n"
332 |         "1. Exactly one sentence, under 22 words.\n"
333 |         f"2. {starter_rule}\n"
334 |         "3. Do NOT restate hotspot titles verbatim.\n"
335 |         "4. Do NOT use any of these banned phrases: " + BANNED_LIST + ".\n"
336 |         "5. Do NOT use the words 'posture', 'subsequent', or 'modernization' anywhere.\n"
337 |         "6. Plain prose. No bullets, no quotes, no headings.\n"
338 |         "7. Reply only inside <answer></answer> tags.\n\n"
339 |         f"Phase: {workstream.phase}\n"
340 |         f"Phase intent: {phase_intent}\n"
341 |         "Hotspots in this phase:\n"
342 |         f"{hotspot_lines}\n\n"
343 |         "<answer>"
344 |     )
345 | 
346 | 
347 | def enrich_with_narratives(scan_result: ScanResult) -> None:
348 |     initialize_watsonx_client()
349 | 
350 |     scan_result.executive_summary = _limit_sentences(
351 |         generate_text(
352 |             build_executive_summary_prompt(scan_result),
353 |             max_tokens=170,
354 |         ),
355 |         3,
356 |     )
357 | 
358 |     for hotspot in scan_result.hotspots:
359 |         hotspot.narrative = _limit_sentences(
360 |             generate_text(
361 |                 build_hotspot_narrative_prompt(hotspot),
362 |                 max_tokens=110,
363 |             ),
364 |             2,
365 |         )
366 | 
367 |     hotspot_lookup = {hotspot.id: hotspot for hotspot in scan_result.hotspots}
368 |     for workstream in scan_result.workstreams:
369 |         grouped_hotspots = [
370 |             hotspot_lookup[hotspot_id]
371 |             for hotspot_id in workstream.hotspot_ids
372 |             if hotspot_id in hotspot_lookup
373 |         ]
374 |         workstream.rationale = _limit_sentences(
375 |             generate_text(
376 |                 build_workstream_rationale_prompt(workstream, grouped_hotspots),
377 |                 max_tokens=60,
378 |             ),
379 |             1,
380 |         )
381 | 
382 | 
383 | def _get_config() -> dict[str, str]:
384 |     api_key = os.getenv("WATSONX_API_KEY")
385 |     project_id = os.getenv("WATSONX_PROJECT_ID")
386 |     url = os.getenv("WATSONX_URL", DEFAULT_WATSONX_URL).rstrip("/")
387 |     model_id = os.getenv("WATSONX_MODEL_ID", DEFAULT_WATSONX_MODEL_ID)
388 | 
389 |     if not api_key or not project_id:
390 |         raise WatsonxUnavailable("watsonx configuration is incomplete")
391 |     if model_id in BANNED_MODELS:
392 |         raise WatsonxUnavailable("watsonx configured model is not permitted")
393 | 
394 |     return {
395 |         "api_key": api_key,
396 |         "project_id": project_id,
397 |         "url": url,
398 |         "model_id": model_id,
399 |     }
400 | 
401 | 
402 | def _normalize_generated_text(value: str) -> str:
403 |     return " ".join(value.strip().split())
404 | 
405 | 
406 | def _extract_answer(value: str) -> str:
407 |     start_tag = "<answer>"
408 |     # Tolerate broken end tags like "</answer" (no closing bracket) or "</answer ".
409 |     end_tag_pattern = re.compile(r"</\s*answer\s*>?", re.IGNORECASE)
410 | 
411 |     start = value.find(start_tag)
412 |     end_match = end_tag_pattern.search(value)
413 |     end = end_match.start() if end_match else -1
414 | 
415 |     if start != -1 and end != -1 and end > start:
416 |         value = value[start + len(start_tag):end]
417 |     elif end != -1:
418 |         # Model emitted only a closing tag (because we pre-seeded <answer>).
419 |         value = value[:end]
420 |     elif start != -1:
421 |         # Open tag with no close — take everything after the open.
422 |         value = value[start + len(start_tag):]
423 | 
424 |     # Belt and braces: strip any residual tag remnants.
425 |     value = end_tag_pattern.sub(" ", value)
426 |     value = value.replace(start_tag, " ")
427 |     value = value.replace("```", " ")
428 |     return value
429 | 
430 | 
431 | def _sanitize(value: str) -> str:
432 |     """Post-hoc replace banned phrases with neutral alternatives."""
433 |     sanitized = value
434 |     for pattern, replacement in SANITIZE_REPLACEMENTS:
435 |         sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
436 |     # Collapse any double spaces from substitutions.
437 |     sanitized = re.sub(r"\s{2,}", " ", sanitized).strip()
438 |     return sanitized
439 | 
440 | 
441 | def _limit_sentences(value: str, count: int) -> str:
442 |     sentences = [
443 |         sentence.strip()
444 |         for sentence in re.split(r"(?<=[.!?])\s+", value)
445 |         if sentence.strip()
446 |     ]
447 |     if not sentences:
448 |         return value.strip()
449 |     return " ".join(sentences[:count]).strip()
</content>
</file>
<file><path>apps/web/src/lib/types.ts</path>
<content lines="1-46">
 1 | export type Severity = 'Critical' | 'High' | 'Medium' | 'Low'
 2 | export type HotspotCategory = 'runtime' | 'architecture' | 'quality'
 3 | export type WorkstreamPhase = 'now' | 'next' | 'later'
 4 | export type ScanStatus = 'started' | 'completed'
 5 | 
 6 | export interface Hotspot {
 7 |   id: string
 8 |   title: string
 9 |   severity: Severity
10 |   category: HotspotCategory
11 |   summary: string
12 |   affected_files: string[]
13 |   recommended_action: string
14 |   cve_id?: string | null
15 |   cvss_score?: number | null
16 |   narrative?: string | null
17 | }
18 | 
19 | export interface Workstream {
20 |   phase: WorkstreamPhase
21 |   hotspot_ids: string[]
22 |   effort: string
23 |   impact: string
24 |   rationale?: string | null
25 | }
26 | 
27 | export interface ScanResult {
28 |   scan_id: string
29 |   repo_url: string
30 |   branch: string
31 |   scenario_id: string | null
32 |   status: ScanStatus
33 |   readiness_score: number
34 |   hotspots: Hotspot[]
35 |   workstreams: Workstream[]
36 |   executive_summary?: string | null
37 | }
38 | 
39 | export interface HandoffPack {
40 |   hotspot_id: string
41 |   title: string
42 |   prompt: string
43 |   target_files: string[]
44 |   acceptance_criteria: string[]
45 |   test_plan: string[]
46 | }
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files


# VSCode Open Tabs


# Current Time
Current time in ISO 8601 UTC format: 2026-05-03T01:16:30.649Z
User time zone: Africa/Tunis, UTC+1:00

# Current Cost
$0.04

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<read_file>
<args>
  <file>
    <path>apps/web/src/App.tsx</path>
  </file>
  <file>
    <path>apps/api/scanners/runner.py</path>
  </file>
  <file>
    <path>apps/api/pyproject.toml</path>
  </file>
  <file>
    <path>apps/web/package.json</path>
  </file>
  <file>
    <path>docker-compose.yml</path>
  </file>
</args>
</read_file>

---

**User:**

[read_file for 5 files] Result:
<files>
<file><path>apps/web/src/App.tsx</path>
<content lines="1-684">
  1 | // /Users/oussama/dev/hackathon/Legacy-Modernization-Radar/apps/web/src/App.tsx
  2 | 
  3 | import { useEffect, useState } from 'react'
  4 | 
  5 | import type {
  6 |   HandoffPack,
  7 |   Hotspot,
  8 |   ScanResult,
  9 |   Workstream,
 10 |   WorkstreamPhase,
 11 | } from './lib/types'
 12 | 
 13 | const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8080'
 14 | const DEFAULT_REPO_URL =
 15 |   'https://github.com/OussamaHorchani/spring-framework-petclinic'
 16 | const DEFAULT_BRANCH = 'legacy-baseline'
 17 | const PHASES: WorkstreamPhase[] = ['now', 'next', 'later']
 18 | 
 19 | type AppScanStatus = 'idle' | 'started' | 'completed'
 20 | 
 21 | const phaseLabels: Record<WorkstreamPhase, string> = {
 22 |   now: 'Now',
 23 |   next: 'Next',
 24 |   later: 'Later',
 25 | }
 26 | 
 27 | const severityStyles: Record<Hotspot['severity'], string> = {
 28 |   Critical: 'border-red-500/60 bg-red-500/10 text-red-100',
 29 |   High: 'border-orange-500/60 bg-orange-500/10 text-orange-100',
 30 |   Medium: 'border-amber-500/60 bg-amber-500/10 text-amber-100',
 31 |   Low: 'border-emerald-500/60 bg-emerald-500/10 text-emerald-100',
 32 | }
 33 | 
 34 | function App() {
 35 |   const [repoUrl, setRepoUrl] = useState(DEFAULT_REPO_URL)
 36 |   const [branch, setBranch] = useState(DEFAULT_BRANCH)
 37 |   const [scanId, setScanId] = useState<string | null>(null)
 38 |   const [scanStatus, setScanStatus] = useState<AppScanStatus>('idle')
 39 |   const [scanResult, setScanResult] = useState<ScanResult | null>(null)
 40 |   const [selectedHotspotId, setSelectedHotspotId] = useState<string | null>(null)
 41 |   const [handoffPack, setHandoffPack] = useState<HandoffPack | null>(null)
 42 |   const [isScanning, setIsScanning] = useState(false)
 43 |   const [isHandoffLoading, setIsHandoffLoading] = useState(false)
 44 |   const [isApproving, setIsApproving] = useState(false)
 45 |   const [approvedHotspotIds, setApprovedHotspotIds] = useState<string[]>([])
 46 |   const [error, setError] = useState<string | null>(null)
 47 | 
 48 |   const selectedHotspot =
 49 |     scanResult?.hotspots.find((hotspot) => hotspot.id === selectedHotspotId) ?? null
 50 | 
 51 |   useEffect(() => {
 52 |     if (!scanId) {
 53 |       return
 54 |     }
 55 | 
 56 |     let cancelled = false
 57 |     let timeoutId: number | undefined
 58 | 
 59 |     const pollScan = async () => {
 60 |       try {
 61 |         const result = await fetchJson<ScanResult>(`${API_URL}/api/scans/${scanId}`)
 62 |         if (cancelled) {
 63 |           return
 64 |         }
 65 | 
 66 |         setScanResult(result)
 67 |         setScanStatus(result.status)
 68 |         setIsScanning(false)
 69 |         setError(null)
 70 | 
 71 |         if (result.status !== 'completed') {
 72 |           timeoutId = window.setTimeout(pollScan, 1500)
 73 |         }
 74 |       } catch (pollError) {
 75 |         if (cancelled) {
 76 |           return
 77 |         }
 78 | 
 79 |         setError(getErrorMessage(pollError))
 80 |         setIsScanning(false)
 81 |         setScanStatus('idle')
 82 |       }
 83 |     }
 84 | 
 85 |     void pollScan()
 86 | 
 87 |     return () => {
 88 |       cancelled = true
 89 |       if (timeoutId) {
 90 |         window.clearTimeout(timeoutId)
 91 |       }
 92 |     }
 93 |   }, [scanId])
 94 | 
 95 |   useEffect(() => {
 96 |     if (!selectedHotspot) {
 97 |       setHandoffPack(null)
 98 |       return
 99 |     }
100 | 
101 |     let cancelled = false
102 | 
103 |     const loadHandoffPack = async () => {
104 |       setIsHandoffLoading(true)
105 | 
106 |       try {
107 |         const pack = await fetchJson<HandoffPack>(
108 |           `${API_URL}/api/hotspots/${selectedHotspot.id}/handoff`,
109 |           {
110 |             method: 'POST',
111 |           },
112 |         )
113 | 
114 |         if (!cancelled) {
115 |           setHandoffPack(pack)
116 |         }
117 |       } catch (handoffError) {
118 |         if (!cancelled) {
119 |           setError(getErrorMessage(handoffError))
120 |         }
121 |       } finally {
122 |         if (!cancelled) {
123 |           setIsHandoffLoading(false)
124 |         }
125 |       }
126 |     }
127 | 
128 |     setHandoffPack(null)
129 |     void loadHandoffPack()
130 | 
131 |     return () => {
132 |       cancelled = true
133 |     }
134 |   }, [selectedHotspot])
135 | 
136 |   const handleScan = async () => {
137 |     const trimmedRepoUrl = repoUrl.trim()
138 |     const trimmedBranch = branch.trim() || 'main'
139 |     if (!trimmedRepoUrl) {
140 |       setError('Enter a repository URL before starting a scan.')
141 |       return
142 |     }
143 | 
144 |     setIsScanning(true)
145 |     setScanStatus('started')
146 |     setScanResult(null)
147 |     setScanId(null)
148 |     setSelectedHotspotId(null)
149 |     setHandoffPack(null)
150 |     setApprovedHotspotIds([])
151 |     setError(null)
152 | 
153 |     try {
154 |       const response = await fetchJson<{ scan_id: string; status: 'started' }>(
155 |         `${API_URL}/api/scans`,
156 |         {
157 |           method: 'POST',
158 |           headers: {
159 |             'Content-Type': 'application/json',
160 |           },
161 |           body: JSON.stringify({
162 |             repo_url: trimmedRepoUrl,
163 |             branch: trimmedBranch,
164 |             scenario_id: null,
165 |           }),
166 |         },
167 |       )
168 | 
169 |       setScanId(response.scan_id)
170 |       setScanStatus(response.status)
171 |     } catch (scanError) {
172 |       setError(getErrorMessage(scanError))
173 |       setIsScanning(false)
174 |       setScanStatus('idle')
175 |     }
176 |   }
177 | 
178 |   const handleApprove = async () => {
179 |     if (!selectedHotspot) {
180 |       return
181 |     }
182 | 
183 |     setIsApproving(true)
184 | 
185 |     try {
186 |       await fetchJson<{ ok: true }>(
187 |         `${API_URL}/api/hotspots/${selectedHotspot.id}/approve`,
188 |         {
189 |           method: 'POST',
190 |         },
191 |       )
192 | 
193 |       setApprovedHotspotIds((current) =>
194 |         current.includes(selectedHotspot.id)
195 |           ? current
196 |           : [...current, selectedHotspot.id],
197 |       )
198 |     } catch (approveError) {
199 |       setError(getErrorMessage(approveError))
200 |     } finally {
201 |       setIsApproving(false)
202 |     }
203 |   }
204 | 
205 |   return (
206 |     <div className="min-h-screen bg-slate-950 text-slate-100">
207 |       <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-6 sm:px-6 lg:px-8">
208 |         <header className="rounded-2xl border border-slate-800 bg-slate-900/90 p-5 shadow-lg shadow-slate-950/30">
209 |           <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
210 |             <div className="space-y-2">
211 |               <p className="text-sm font-medium uppercase tracking-[0.22em] text-slate-400">
212 |                 Control Tower
213 |               </p>
214 |               <h1 className="text-3xl font-semibold text-white sm:text-4xl">
215 |                 Legacy Modernization Radar
216 |               </h1>
217 |               <p className="max-w-3xl text-sm text-slate-400 sm:text-base">
218 |                 Scan a legacy repository, rank its modernization hotspots, and
219 |                 prepare one approved handoff for IBM Bob.
220 |               </p>
221 |             </div>
222 | 
223 |             <div className="flex w-full flex-col gap-3 lg:max-w-3xl">
224 |               <div className="flex flex-col gap-3 sm:flex-row">
225 |                 <label className="sr-only" htmlFor="repo-url">
226 |                   Repository URL
227 |                 </label>
228 |                 <input
229 |                   id="repo-url"
230 |                   type="url"
231 |                   value={repoUrl}
232 |                   onChange={(event) => setRepoUrl(event.target.value)}
233 |                   placeholder="https://github.com/org/repo"
234 |                   className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-500/30"
235 |                 />
236 |                 <label className="sr-only" htmlFor="branch">
237 |                   Branch
238 |                 </label>
239 |                 <input
240 |                   id="branch"
241 |                   type="text"
242 |                   value={branch}
243 |                   onChange={(event) => setBranch(event.target.value)}
244 |                   placeholder="branch"
245 |                   className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-500/30 sm:max-w-[14rem]"
246 |                 />
247 |                 <button
248 |                   type="button"
249 |                   onClick={handleScan}
250 |                   disabled={isScanning}
251 |                   className="rounded-xl bg-sky-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300"
252 |                 >
253 |                   {isScanning ? 'Scanning...' : 'Scan'}
254 |                 </button>
255 |               </div>
256 |             </div>
257 |           </div>
258 | 
259 |           <div className="mt-4 flex flex-wrap gap-3 text-sm text-slate-400">
260 |             <span>API: {API_URL}</span>
261 |             <span>
262 |               Status:{' '}
263 |               {scanStatus === 'idle'
264 |                 ? 'Idle'
265 |                 : scanStatus === 'started'
266 |                   ? 'Scan started'
267 |                   : 'Scan completed'}
268 |             </span>
269 |             {scanId ? <span>Scan ID: {scanId}</span> : null}
270 |           </div>
271 | 
272 |           {error ? (
273 |             <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-100">
274 |               {error}
275 |             </div>
276 |           ) : null}
277 |         </header>
278 | 
279 |         <main className="mt-6 grid flex-1 gap-6">
280 |           <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
281 |             <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
282 |               <div>
283 |                 <h2 className="text-lg font-semibold text-white">
284 |                   Readiness Score
285 |                 </h2>
286 |                 <p className="mt-1 text-sm text-slate-400">
287 |                   Composite score across runtime, architecture, and quality risk.
288 |                 </p>
289 |               </div>
290 |               {scanResult ? (
291 |                 <p className="text-sm text-slate-400">
292 |                   Branch <span className="font-mono text-slate-200">{scanResult.branch}</span>
293 |                 </p>
294 |               ) : null}
295 |             </div>
296 | 
297 |             <div className="mt-6 flex items-end gap-4">
298 |               <div className="text-6xl font-semibold text-white sm:text-7xl">
299 |                 {scanResult?.readiness_score ?? '--'}
300 |               </div>
301 |               <div className="pb-2 text-sm uppercase tracking-[0.2em] text-slate-500">
302 |                 / 100
303 |               </div>
304 |             </div>
305 | 
306 |             {scanResult?.executive_summary ? (
307 |               <p className="mt-5 max-w-3xl text-sm leading-7 text-slate-300">
308 |                 {scanResult.executive_summary}
309 |               </p>
310 |             ) : null}
311 |           </section>
312 | 
313 |           <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
314 |             <div className="flex items-center justify-between gap-4">
315 |               <div>
316 |                 <h2 className="text-lg font-semibold text-white">
317 |                   Hotspot Heatmap
318 |                 </h2>
319 |                 <p className="mt-1 text-sm text-slate-400">
320 |                   Click a hotspot to inspect details and preview the handoff pack.
321 |                 </p>
322 |               </div>
323 |               {scanResult ? (
324 |                 <p className="text-sm text-slate-400">
325 |                   {scanResult.hotspots.length} hotspots
326 |                 </p>
327 |               ) : null}
328 |             </div>
329 | 
330 |             {scanResult ? (
331 |               <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
332 |                 {scanResult.hotspots.map((hotspot) => {
333 |                   const isSelected = selectedHotspotId === hotspot.id
334 |                   const isApproved = approvedHotspotIds.includes(hotspot.id)
335 | 
336 |                   return (
337 |                     <button
338 |                       key={hotspot.id}
339 |                       type="button"
340 |                       onClick={() => setSelectedHotspotId(hotspot.id)}
341 |                       className={`rounded-2xl border p-5 text-left transition hover:border-sky-500/60 hover:bg-slate-800 ${
342 |                         isSelected ? 'border-sky-500 bg-slate-800' : 'border-slate-800 bg-slate-950'
343 |                       }`}
344 |                     >
345 |                       <div className="flex items-start justify-between gap-3">
346 |                         <span
347 |                           className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${severityStyles[hotspot.severity]}`}
348 |                         >
349 |                           {hotspot.severity}
350 |                         </span>
351 |                         {isApproved ? (
352 |                           <span className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-200">
353 |                             Approved
354 |                           </span>
355 |                         ) : null}
356 |                       </div>
357 | 
358 |                       <h3 className="mt-4 text-base font-semibold text-white">
359 |                         {hotspot.title}
360 |                       </h3>
361 |                       <p className="mt-3 text-sm leading-6 text-slate-300">
362 |                         {hotspot.summary}
363 |                       </p>
364 | 
365 |                       {hotspot.narrative ? (
366 |                         <div className="mt-4 border-t border-slate-800 pt-4">
367 |                           <p className="text-sm leading-6 text-slate-400 italic">
368 |                             {hotspot.narrative}
369 |                           </p>
370 |                         </div>
371 |                       ) : null}
372 | 
373 |                       <div className="mt-4 flex items-center justify-between text-sm text-slate-400">
374 |                         <span className="capitalize">{hotspot.category}</span>
375 |                         <span>{hotspot.affected_files.length} files</span>
376 |                       </div>
377 |                     </button>
378 |                   )
379 |                 })}
380 |               </div>
381 |             ) : (
382 |               <EmptyState message="Run a scan to populate readiness, hotspots, and roadmap recommendations." />
383 |             )}
384 |           </section>
385 | 
386 |           <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
387 |             <div>
388 |               <h2 className="text-lg font-semibold text-white">Phased Roadmap</h2>
389 |               <p className="mt-1 text-sm text-slate-400">
390 |                 Workstreams grouped by when they should land.
391 |               </p>
392 |             </div>
393 | 
394 |             {scanResult ? (
395 |               <div className="mt-6 grid gap-4 lg:grid-cols-3">
396 |                 {PHASES.map((phase) => (
397 |                   <RoadmapColumn
398 |                     key={phase}
399 |                     phase={phase}
400 |                     workstreams={scanResult.workstreams}
401 |                     hotspots={scanResult.hotspots}
402 |                   />
403 |                 ))}
404 |               </div>
405 |             ) : (
406 |               <EmptyState message="The roadmap will appear here after the first scan completes." />
407 |             )}
408 |           </section>
409 |         </main>
410 |       </div>
411 | 
412 |       <div
413 |         className={`fixed inset-0 z-40 bg-slate-950/70 transition-opacity ${
414 |           selectedHotspot ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
415 |         }`}
416 |         onClick={() => setSelectedHotspotId(null)}
417 |       />
418 | 
419 |       <aside
420 |         className={`fixed right-0 top-0 z-50 h-full w-full max-w-2xl transform overflow-y-auto border-l border-slate-800 bg-slate-900 shadow-2xl shadow-black/50 transition-transform duration-200 sm:w-[42rem] ${
421 |           selectedHotspot ? 'translate-x-0' : 'translate-x-full'
422 |         }`}
423 |       >
424 |         <div className="flex min-h-full flex-col">
425 |           <div className="flex items-start justify-between gap-4 border-b border-slate-800 px-6 py-5">
426 |             <div>
427 |               <p className="text-sm uppercase tracking-[0.2em] text-slate-500">
428 |                 Hotspot Details
429 |               </p>
430 |               <h2 className="mt-2 text-xl font-semibold text-white">
431 |                 {selectedHotspot?.title ?? 'No hotspot selected'}
432 |               </h2>
433 |             </div>
434 |             <button
435 |               type="button"
436 |               onClick={() => setSelectedHotspotId(null)}
437 |               className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:border-slate-500 hover:text-white"
438 |             >
439 |               Close
440 |             </button>
441 |           </div>
442 | 
443 |           {selectedHotspot ? (
444 |             <div className="flex-1 space-y-6 px-6 py-5">
445 |               <div className="flex flex-wrap items-center gap-3">
446 |                 <span
447 |                   className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${severityStyles[selectedHotspot.severity]}`}
448 |                 >
449 |                   {selectedHotspot.severity}
450 |                 </span>
451 |                 <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-medium capitalize text-slate-300">
452 |                   {selectedHotspot.category}
453 |                 </span>
454 |               </div>
455 | 
456 |               <div className="space-y-3">
457 |                 <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
458 |                   Summary
459 |                 </h3>
460 |                 <p className="text-sm leading-7 text-slate-200">
461 |                   {selectedHotspot.summary}
462 |                 </p>
463 |               </div>
464 | 
465 |               <div className="space-y-3">
466 |                 <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
467 |                   Recommended Action
468 |                 </h3>
469 |                 <p className="text-sm leading-7 text-slate-200">
470 |                   {selectedHotspot.recommended_action}
471 |                 </p>
472 |               </div>
473 | 
474 |               <div className="space-y-3">
475 |                 <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
476 |                   Affected Files
477 |                 </h3>
478 |                 <div className="space-y-2">
479 |                   {selectedHotspot.affected_files.map((file) => (
480 |                     <div
481 |                       key={file}
482 |                       className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 font-mono text-sm text-slate-200"
483 |                     >
484 |                       {file}
485 |                     </div>
486 |                   ))}
487 |                 </div>
488 |               </div>
489 | 
490 |               <div className="flex flex-wrap items-center gap-3">
491 |                 <button
492 |                   type="button"
493 |                   onClick={handleApprove}
494 |                   disabled={isApproving}
495 |                   className="rounded-xl bg-emerald-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300"
496 |                 >
497 |                   {approvedHotspotIds.includes(selectedHotspot.id)
498 |                     ? 'Approved'
499 |                     : isApproving
500 |                       ? 'Approving...'
501 |                       : 'Approve'}
502 |                 </button>
503 |               </div>
504 | 
505 |               <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-950 p-5">
506 |                 <div>
507 |                   <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
508 |                     Handoff Pack Preview
509 |                   </h3>
510 |                   <p className="mt-1 text-sm text-slate-500">
511 |                     Structured prompt the Radar will send to IBM Bob for execution.
512 |                   </p>
513 |                 </div>
514 | 
515 |                 {isHandoffLoading ? (
516 |                   <p className="text-sm text-slate-300">Loading handoff pack...</p>
517 |                 ) : handoffPack ? (
518 |                   <div className="space-y-5">
519 |                     <div className="space-y-2">
520 |                       <h4 className="text-base font-semibold text-white">
521 |                         {handoffPack.title}
522 |                       </h4>
523 |                       <p className="text-sm leading-7 text-slate-200">
524 |                         {handoffPack.prompt}
525 |                       </p>
526 |                     </div>
527 | 
528 |                     <div>
529 |                       <h5 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
530 |                         Target Files
531 |                       </h5>
532 |                       <div className="mt-3 space-y-2">
533 |                         {handoffPack.target_files.map((file) => (
534 |                           <div
535 |                             key={file}
536 |                             className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 font-mono text-sm text-slate-200"
537 |                           >
538 |                             {file}
539 |                           </div>
540 |                         ))}
541 |                       </div>
542 |                     </div>
543 | 
544 |                     <ListBlock
545 |                       title="Acceptance Criteria"
546 |                       items={handoffPack.acceptance_criteria}
547 |                     />
548 |                     <ListBlock title="Test Plan" items={handoffPack.test_plan} />
549 |                   </div>
550 |                 ) : (
551 |                   <p className="text-sm text-slate-300">
552 |                     Select a hotspot to preview its handoff guidance.
553 |                   </p>
554 |                 )}
555 |               </div>
556 |             </div>
557 |           ) : (
558 |             <div className="flex flex-1 items-center justify-center px-6 py-10 text-center text-sm text-slate-400">
559 |               Choose a hotspot from the heatmap to inspect its details.
560 |             </div>
561 |           )}
562 |         </div>
563 |       </aside>
564 |     </div>
565 |   )
566 | }
567 | 
568 | function RoadmapColumn({
569 |   phase,
570 |   workstreams,
571 |   hotspots,
572 | }: {
573 |   phase: WorkstreamPhase
574 |   workstreams: Workstream[]
575 |   hotspots: Hotspot[]
576 | }) {
577 |   const phaseWorkstreams = workstreams.filter((workstream) => workstream.phase === phase)
578 | 
579 |   return (
580 |     <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
581 |       <div className="flex items-center justify-between gap-3">
582 |         <h3 className="text-base font-semibold text-white">{phaseLabels[phase]}</h3>
583 |         <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-medium text-slate-300">
584 |           {phaseWorkstreams.length} workstream{phaseWorkstreams.length === 1 ? '' : 's'}
585 |         </span>
586 |       </div>
587 | 
588 |       {phaseWorkstreams[0]?.rationale ? (
589 |         <p className="mt-3 text-sm leading-6 text-slate-400 italic">
590 |           {phaseWorkstreams[0].rationale}
591 |         </p>
592 |       ) : null}
593 | 
594 |       <div className="mt-4 space-y-4">
595 |         {phaseWorkstreams.map((workstream) => (
596 |           <div
597 |             key={`${phase}-${workstream.impact}`}
598 |             className="rounded-xl border border-slate-800 bg-slate-900 p-4"
599 |           >
600 |             <div className="flex items-center justify-between gap-4 text-sm text-slate-400">
601 |               <span>Effort {workstream.effort}</span>
602 |               <span>{workstream.hotspot_ids.length} hotspot{workstream.hotspot_ids.length === 1 ? '' : 's'}</span>
603 |             </div>
604 |             <p className="mt-3 text-sm leading-6 text-slate-200">
605 |               {workstream.impact}
606 |             </p>
607 |             <div className="mt-4 space-y-2">
608 |               {workstream.hotspot_ids.map((hotspotId) => {
609 |                 const hotspot = hotspots.find((item) => item.id === hotspotId)
610 |                 if (!hotspot) {
611 |                   return null
612 |                 }
613 | 
614 |                 return (
615 |                   <div
616 |                     key={hotspot.id}
617 |                     className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3"
618 |                   >
619 |                     <p className="text-sm font-medium text-white">{hotspot.title}</p>
620 |                     <p className="mt-1 text-sm text-slate-400">
621 |                       {hotspot.severity} · {hotspot.category}
622 |                     </p>
623 |                   </div>
624 |                 )
625 |               })}
626 |             </div>
627 |           </div>
628 |         ))}
629 | 
630 |         {phaseWorkstreams.length === 0 ? (
631 |           <p className="text-sm text-slate-400">No workstreams assigned.</p>
632 |         ) : null}
633 |       </div>
634 |     </div>
635 |   )
636 | }
637 | 
638 | function ListBlock({ title, items }: { title: string; items: string[] }) {
639 |   return (
640 |     <div>
641 |       <h5 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
642 |         {title}
643 |       </h5>
644 |       <ul className="mt-3 space-y-2">
645 |         {items.map((item) => (
646 |           <li
647 |             key={item}
648 |             className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm leading-6 text-slate-200"
649 |           >
650 |             {item}
651 |           </li>
652 |         ))}
653 |       </ul>
654 |     </div>
655 |   )
656 | }
657 | 
658 | function EmptyState({ message }: { message: string }) {
659 |   return (
660 |     <div className="mt-6 rounded-2xl border border-dashed border-slate-700 bg-slate-950 px-4 py-10 text-center text-sm text-slate-400">
661 |       {message}
662 |     </div>
663 |   )
664 | }
665 | 
666 | async function fetchJson<T>(input: string, init?: RequestInit): Promise<T> {
667 |   const response = await fetch(input, init)
668 | 
669 |   if (!response.ok) {
670 |     throw new Error(`Request failed with status ${response.status}`)
671 |   }
672 | 
673 |   return (await response.json()) as T
674 | }
675 | 
676 | function getErrorMessage(error: unknown): string {
677 |   if (error instanceof Error) {
678 |     return error.message
679 |   }
680 | 
681 |   return 'Something went wrong while talking to the API.'
682 | }
683 | 
684 | export default App
</content>
</file>
<file><path>apps/api/scanners/runner.py</path>
<content lines="1-138">
  1 | import logging
  2 | from pathlib import Path
  3 | 
  4 | from llm import WatsonxUnavailable, enrich_with_narratives
  5 | from schema import Hotspot, ScanResult, Workstream
  6 | 
  7 | from scanners import sort_hotspots
  8 | from scanners.clone import CloneError, shallow_clone
  9 | from scanners.complex_methods import scan_complex_methods
 10 | from scanners.dependency_cve import scan_dependencies
 11 | from scanners.test_coverage import scan_test_coverage
 12 | 
 13 | SEVERITY_TO_PHASE = {
 14 |     "Critical": "now",
 15 |     "High": "next",
 16 |     "Medium": "later",
 17 |     "Low": "later",
 18 | }
 19 | 
 20 | WORKSTREAM_TEMPLATES = {
 21 |     "Critical": (
 22 |         "0.5-1 day",
 23 |         "Removes the most urgent runtime or supply-chain risk before broader rollout.",
 24 |     ),
 25 |     "High": (
 26 |         "1-2 days",
 27 |         "Stabilizes a risky implementation path before deeper modernization changes.",
 28 |     ),
 29 |     "Medium": (
 30 |         "0.5-1 day",
 31 |         "Backfills quality guardrails to reduce regression risk during follow-on work.",
 32 |     ),
 33 |     "Low": (
 34 |         "0.5 day",
 35 |         "Cleans up lower-severity issues that can be folded into later hardening work.",
 36 |     ),
 37 | }
 38 | 
 39 | SEVERITY_PENALTIES = {
 40 |     "Critical": 25,
 41 |     "High": 15,
 42 |     "Medium": 5,
 43 |     "Low": 1,
 44 | }
 45 | 
 46 | logger = logging.getLogger("uvicorn.error")
 47 | 
 48 | 
 49 | def run_scan(repo_url: str, branch: str) -> ScanResult:
 50 |     try:
 51 |         with shallow_clone(repo_url, branch) as repo_path:
 52 |             hotspots = _run_detectors(repo_path)
 53 |     except CloneError:
 54 |         return ScanResult(
 55 |             scan_id="",
 56 |             repo_url=repo_url,
 57 |             branch=branch,
 58 |             readiness_score=0,
 59 |             hotspots=[],
 60 |             workstreams=[],
 61 |         )
 62 |     except Exception:
 63 |         return ScanResult(
 64 |             scan_id="",
 65 |             repo_url=repo_url,
 66 |             branch=branch,
 67 |             readiness_score=0,
 68 |             hotspots=[],
 69 |             workstreams=[],
 70 |         )
 71 | 
 72 |     ordered_hotspots = sort_hotspots(_dedupe_hotspots(hotspots))
 73 |     result = ScanResult(
 74 |         scan_id="",
 75 |         repo_url=repo_url,
 76 |         branch=branch,
 77 |         readiness_score=calculate_readiness(ordered_hotspots) if ordered_hotspots else 100,
 78 |         hotspots=ordered_hotspots,
 79 |         workstreams=group_into_workstreams(ordered_hotspots),
 80 |     )
 81 | 
 82 |     try:
 83 |         enrich_with_narratives(result)
 84 |     except WatsonxUnavailable as exc:
 85 |         logger.warning(
 86 |             "watsonx.ai unavailable, returning deterministic result",
 87 |             extra={"reason": str(exc)},
 88 |         )
 89 | 
 90 |     return result
 91 | 
 92 | 
 93 | def calculate_readiness(hotspots: list[Hotspot]) -> int:
 94 |     score = 100
 95 |     for hotspot in hotspots:
 96 |         score -= SEVERITY_PENALTIES[hotspot.severity]
 97 |     return max(score, 0)
 98 | 
 99 | 
100 | def group_into_workstreams(hotspots: list[Hotspot]) -> list[Workstream]:
101 |     grouped: dict[str, list[Hotspot]] = {"now": [], "next": [], "later": []}
102 |     for hotspot in hotspots:
103 |         grouped[SEVERITY_TO_PHASE[hotspot.severity]].append(hotspot)
104 | 
105 |     workstreams: list[Workstream] = []
106 |     for phase in ("now", "next", "later"):
107 |         phase_hotspots = grouped[phase]
108 |         if not phase_hotspots:
109 |             continue
110 | 
111 |         template = WORKSTREAM_TEMPLATES[phase_hotspots[0].severity]
112 |         workstreams.append(
113 |             Workstream(
114 |                 phase=phase,
115 |                 hotspot_ids=[hotspot.id for hotspot in phase_hotspots],
116 |                 effort=template[0],
117 |                 impact=template[1],
118 |             )
119 |         )
120 | 
121 |     return workstreams
122 | 
123 | 
124 | def _run_detectors(repo_path: Path) -> list[Hotspot]:
125 |     hotspots: list[Hotspot] = []
126 |     for detector in (scan_dependencies, scan_test_coverage, scan_complex_methods):
127 |         try:
128 |             hotspots.extend(detector(repo_path))
129 |         except Exception:
130 |             continue
131 |     return hotspots
132 | 
133 | 
134 | def _dedupe_hotspots(hotspots: list[Hotspot]) -> list[Hotspot]:
135 |     unique: dict[str, Hotspot] = {}
136 |     for hotspot in hotspots:
137 |         unique[hotspot.id] = hotspot
138 |     return list(unique.values())
</content>
</file>
<file><path>apps/api/pyproject.toml</path>
<content lines="1-21">
 1 | [build-system]
 2 | requires = ["setuptools>=68", "wheel"]
 3 | build-backend = "setuptools.build_meta"
 4 | 
 5 | [project]
 6 | name = "legacy-modernization-radar-api"
 7 | version = "0.1.0"
 8 | description = "FastAPI backend for the Legacy Modernization Radar hackathon app"
 9 | requires-python = ">=3.11"
10 | dependencies = [
11 |   "fastapi",
12 |   "uvicorn[standard]",
13 |   "pydantic>=2",
14 |   "httpx",
15 |   "python-dotenv",
16 |   "python-multipart",
17 | ]
18 | 
19 | [tool.setuptools]
20 | packages = ["scanners"]
21 | py-modules = ["llm", "main", "schema"]
</content>
</file>
<file><path>apps/web/package.json</path>
<content lines="1-34">
 1 | {
 2 |   "name": "web",
 3 |   "private": true,
 4 |   "version": "0.0.0",
 5 |   "type": "module",
 6 |   "scripts": {
 7 |     "dev": "vite",
 8 |     "build": "tsc -b && vite build",
 9 |     "lint": "eslint .",
10 |     "preview": "vite preview"
11 |   },
12 |   "dependencies": {
13 |     "react": "^19.2.5",
14 |     "react-dom": "^19.2.5"
15 |   },
16 |   "devDependencies": {
17 |     "@eslint/js": "^10.0.1",
18 |     "@tailwindcss/vite": "^4.2.4",
19 |     "@types/node": "^24.12.2",
20 |     "@types/react": "^19.2.14",
21 |     "@types/react-dom": "^19.2.3",
22 |     "@vitejs/plugin-react": "^6.0.1",
23 |     "autoprefixer": "^10.5.0",
24 |     "eslint": "^10.2.1",
25 |     "eslint-plugin-react-hooks": "^7.1.1",
26 |     "eslint-plugin-react-refresh": "^0.5.2",
27 |     "globals": "^17.5.0",
28 |     "postcss": "^8.5.13",
29 |     "tailwindcss": "^4.2.4",
30 |     "typescript": "~6.0.2",
31 |     "typescript-eslint": "^8.58.2",
32 |     "vite": "^8.0.10"
33 |   }
34 | }
</content>
</file>
<file><path>docker-compose.yml</path>
<content lines="1-21">
 1 | services:
 2 |   api:
 3 |     build:
 4 |       context: ./apps/api
 5 |     environment:
 6 |       PORT: 8080
 7 |       CORS_ORIGINS: http://localhost:5173,http://localhost:8081,*
 8 |     ports:
 9 |       - "8080:8080"
10 | 
11 |   web:
12 |     build:
13 |       context: ./apps/web
14 |       args:
15 |         VITE_API_URL: http://localhost:8080
16 |     depends_on:
17 |       - api
18 |     environment:
19 |       PORT: 8080
20 |     ports:
21 |       - "8081:8080"
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files


# VSCode Open Tabs


# Current Time
Current time in ISO 8601 UTC format: 2026-05-03T01:16:42.109Z
User time zone: Africa/Tunis, UTC+1:00

# Current Cost
$0.10

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<read_file>
<args>
  <file>
    <path>apps/api/fly.toml</path>
  </file>
  <file>
    <path>apps/web/.env.production</path>
  </file>
  <file>
    <path>apps/api/scanners/__init__.py</path>
  </file>
  <file>
    <path>apps/api/Dockerfile</path>
  </file>
  <file>
    <path>apps/web/Dockerfile</path>
  </file>
</args>
</read_file>

---

**User:**

[read_file for 5 files] Result:
<files>
<file><path>apps/api/fly.toml</path>
<content lines="1-34">
 1 | # fly.toml app configuration file generated for legacy-radar-api on 2026-05-02T23:58:30+01:00
 2 | #
 3 | # See https://fly.io/docs/reference/configuration/ for information about how to use this file.
 4 | #
 5 | 
 6 | app = 'legacy-radar-api'
 7 | primary_region = 'iad'
 8 | 
 9 | [build]
10 |   dockerfile = 'Dockerfile'
11 | 
12 | [env]
13 |   CORS_ORIGINS = '*'
14 |   PORT = '8080'
15 | 
16 | [http_service]
17 |   internal_port = 8080
18 |   force_https = true
19 |   auto_stop_machines = 'stop'
20 |   auto_start_machines = true
21 |   min_machines_running = 0
22 |   processes = ['app']
23 | 
24 |   [[http_service.checks]]
25 |     interval = '30s'
26 |     timeout = '5s'
27 |     grace_period = '10s'
28 |     method = 'GET'
29 |     path = '/health'
30 | 
31 | [[vm]]
32 |   cpu_kind = 'shared'
33 |   cpus = 1
34 |   memory_mb = 512
</content>
</file>
<file><path>apps/web/.env.production</path>
<content lines="1-1">
1 | VITE_API_URL=https://legacy-radar-api.fly.dev
</content>
</file>
<file><path>apps/api/scanners/__init__.py</path>
<content lines="1-26">
 1 | from hashlib import sha1
 2 | 
 3 | from schema import Hotspot
 4 | 
 5 | SEVERITY_ORDER = {
 6 |     "Critical": 0,
 7 |     "High": 1,
 8 |     "Medium": 2,
 9 |     "Low": 3,
10 | }
11 | 
12 | 
13 | def make_hotspot_id(category: str, title: str) -> str:
14 |     digest = sha1(f"{category}:{title}".encode("utf-8")).hexdigest()[:12]
15 |     return f"hotspot-{category}-{digest}"
16 | 
17 | 
18 | def sort_hotspots(hotspots: list[Hotspot]) -> list[Hotspot]:
19 |     return sorted(
20 |         hotspots,
21 |         key=lambda hotspot: (
22 |             SEVERITY_ORDER[hotspot.severity],
23 |             hotspot.title.lower(),
24 |             hotspot.id,
25 |         ),
26 |     )
</content>
</file>
<file><path>apps/api/Dockerfile</path>
<content lines="1-44">
 1 | FROM python:3.11-slim AS builder
 2 | 
 3 | ENV PYTHONDONTWRITEBYTECODE=1 \
 4 |     PYTHONUNBUFFERED=1 \
 5 |     PATH="/opt/venv/bin:$PATH"
 6 | 
 7 | WORKDIR /app
 8 | 
 9 | COPY pyproject.toml ./
10 | COPY llm.py main.py schema.py ./
11 | COPY scanners ./scanners
12 | 
13 | RUN python -m venv /opt/venv \
14 |     && /opt/venv/bin/pip install --upgrade pip \
15 |     && /opt/venv/bin/pip install .
16 | 
17 | 
18 | FROM python:3.11-slim AS runtime
19 | 
20 | ENV PYTHONDONTWRITEBYTECODE=1 \
21 |     PYTHONUNBUFFERED=1 \
22 |     PATH="/opt/venv/bin:$PATH" \
23 |     PORT=8080
24 | 
25 | WORKDIR /app
26 | 
27 | RUN apt-get update \
28 |     && apt-get install -y --no-install-recommends git ca-certificates \
29 |     && rm -rf /var/lib/apt/lists/* \
30 |     && addgroup --system app \
31 |     && adduser --system --ingroup app app
32 | 
33 | COPY --from=builder /opt/venv /opt/venv
34 | COPY llm.py main.py schema.py ./
35 | COPY scanners ./scanners
36 | 
37 | USER app
38 | 
39 | EXPOSE 8080
40 | 
41 | HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
42 |   CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\", \"8080\")}/health', timeout=3).read()" || exit 1
43 | 
44 | CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
</content>
</file>
<file><path>apps/web/Dockerfile</path>
<content lines="1-22">
 1 | FROM node:20-alpine AS build
 2 | 
 3 | WORKDIR /app
 4 | 
 5 | ARG VITE_API_URL=http://localhost:8080
 6 | ENV VITE_API_URL=$VITE_API_URL
 7 | 
 8 | COPY package.json package-lock.json ./
 9 | RUN npm ci
10 | 
11 | COPY . .
12 | RUN npm run build
13 | 
14 | 
15 | FROM nginx:alpine AS runtime
16 | 
17 | ENV PORT=8080
18 | 
19 | COPY nginx.conf /etc/nginx/templates/default.conf.template
20 | COPY --from=build /app/dist /usr/share/nginx/html
21 | 
22 | EXPOSE 8080
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files


# VSCode Open Tabs


# Current Time
Current time in ISO 8601 UTC format: 2026-05-03T01:16:49.538Z
User time zone: Africa/Tunis, UTC+1:00

# Current Cost
$0.20

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<update_todo_list>
<todos>
[x] Read project files to understand architecture and implementation
[x] Gather information about scanner detectors and LLM integration
[x] Review deployment configuration and environment variables
[-] Create comprehensive AGENTS.md file with all required sections
[ ] Review and validate the documentation
</todos>
</update_todo_list>

Now I'll create the comprehensive AGENTS.md file based on all the information I've gathered:

<write_to_file>
<path>AGENTS.md</path>
<content># Legacy Modernization Radar — Agent Documentation

## Project Overview

**Legacy Modernization Radar** is a control-tower web application built for the IBM Bob Dev Day Hackathon (May 1-3, 2026). It scans legacy repositories, ranks modernization hotspots by severity and category, and generates a structured handoff pack for IBM Bob to execute one approved fix with passing tests.

### Target Users
Engineering leaders and technical staff who need to prioritize modernization work across legacy codebases without manually auditing every file.

### Key User Flow
1. **Paste repository URL** → User enters a GitHub repository URL and branch name in the web UI
2. **See scan results** → The Radar clones the repo, runs deterministic detectors, enriches findings with watsonx.ai narratives, and displays:
   - Readiness score (0-100)
   - Hotspot heatmap (categorized by severity: Critical, High, Medium, Low)
   - Phased roadmap (now, next, later workstreams)
   - Executive summary
3. **Click hotspot** → User selects a hotspot to view details, affected files, and recommended action
4. **Preview Bob handoff pack** → User sees the structured prompt, target files, acceptance criteria, and test plan that will be sent to IBM Bob
5. **Approve** → User approves the hotspot, signaling readiness to hand off to Bob for execution

---

## Architecture

### Monorepo Layout

```
Legacy-Modernization-Radar/
├── apps/
│   ├── api/              # FastAPI backend (Python 3.11)
│   │   ├── main.py       # FastAPI app, endpoints, in-memory scan cache
│   │   ├── schema.py     # Pydantic models (source of truth for types)
│   │   ├── llm.py        # watsonx.ai integration with fallback handling
│   │   ├── scanners/     # Detector pipeline
│   │   │   ├── __init__.py
│   │   │   ├── runner.py          # Orchestrates detectors, groups workstreams
│   │   │   ├── clone.py           # Shallow git clone utility
│   │   │   ├── dependency_cve.py  # CVE detector (placeholder)
│   │   │   ├── test_coverage.py   # Test coverage detector (placeholder)
│   │   │   └── complex_methods.py # Cyclomatic complexity detector (placeholder)
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── fly.toml      # Fly.io deployment config
│   └── web/              # Vite + React + TypeScript + Tailwind frontend
│       ├── src/
│       │   ├── App.tsx   # Main UI component (scan form, heatmap, roadmap, handoff preview)
│       │   ├── lib/
│       │   │   └── types.ts  # TypeScript types mirroring schema.py
│       │   ├── main.tsx
│       │   └── index.css
│       ├── package.json
│       ├── Dockerfile
│       └── .env.production  # VITE_API_URL for Vercel deploy
├── docker-compose.yml
└── README.md
```

### Communication Between API and Web

- **API** exposes REST endpoints at `http://localhost:8080` (dev) or `https://legacy-radar-api.fly.dev` (prod)
- **Web** polls the API for scan results every 1.5 seconds until status is `completed`
- **No websockets** — polling is simpler for a hackathon demo and avoids connection management complexity
- **CORS** is configured in [`apps/api/main.py`](apps/api/main.py) via `CORS_ORIGINS` environment variable

### Key Modules

#### Scanner Detector Pipeline ([`apps/api/scanners/`](apps/api/scanners/))

- **[`runner.py`](apps/api/scanners/runner.py)**: Orchestrates the scan lifecycle
  - Clones the repository using [`clone.py`](apps/api/scanners/clone.py)
  - Runs all detectors in sequence: `scan_dependencies`, `scan_test_coverage`, `scan_complex_methods`
  - Deduplicates hotspots by ID
  - Sorts hotspots by severity (Critical → High → Medium → Low)
  - Calculates readiness score (100 minus severity penalties)
  - Groups hotspots into workstreams by phase (now, next, later)
  - Calls `enrich_with_narratives()` to add watsonx.ai-generated text
  - Returns a `ScanResult` object

- **[`__init__.py`](apps/api/scanners/__init__.py)**: Utility functions
  - `make_hotspot_id()`: Generates deterministic IDs from category and title
  - `sort_hotspots()`: Sorts by severity order, then title, then ID

- **Detectors** ([`dependency_cve.py`](apps/api/scanners/dependency_cve.py), [`test_coverage.py`](apps/api/scanners/test_coverage.py), [`complex_methods.py`](apps/api/scanners/complex_methods.py)):
  - Each detector scans the cloned repository and returns a list of `Hotspot` objects
  - Detectors are **deterministic** — they analyze code structure, dependencies, and metadata without LLM inference
  - Currently placeholder implementations for hackathon demo

#### watsonx.ai Narrative Integration ([`apps/api/llm.py`](apps/api/llm.py))

- **Purpose**: Enrich scan results with human-readable narratives generated by IBM Granite models
- **Key functions**:
  - `initialize_watsonx_client()`: Validates configuration on startup
  - `get_iam_token()`: Fetches and caches IBM Cloud IAM token (refreshes 5 minutes before expiration)
  - `generate_text()`: Calls watsonx.ai text generation API with greedy decoding
  - `enrich_with_narratives()`: Generates executive summary, hotspot narratives, and workstream rationales
- **Fallback behavior**: If watsonx.ai is unavailable (missing credentials, network error, timeout), the app logs a warning and returns deterministic results without narratives. **The demo never breaks.**

#### Schema ([`apps/api/schema.py`](apps/api/schema.py) ↔ [`apps/web/src/lib/types.ts`](apps/web/src/lib/types.ts))

- **Pydantic models** in `schema.py` define the API contract:
  - `Hotspot`: A single modernization issue (id, title, severity, category, summary, affected_files, recommended_action, optional CVE fields, optional narrative)
  - `Workstream`: A group of hotspots in a phase (now/next/later) with effort estimate and impact description
  - `ScanResult`: Complete scan output (scan_id, repo_url, branch, readiness_score, hotspots, workstreams, optional executive_summary)
  - `HandoffPack`: Structured prompt for IBM Bob (hotspot_id, title, prompt, target_files, acceptance_criteria, test_plan)
- **TypeScript types** in `types.ts` mirror these models exactly
- **Manual sync required** — changes to `schema.py` must be manually reflected in `types.ts`

#### Main UI Component ([`apps/web/src/App.tsx`](apps/web/src/App.tsx))

- **Single-page React app** with no routing
- **State management**: React hooks (`useState`, `useEffect`)
- **Polling logic**: `useEffect` hook polls `/api/scans/{scan_id}` every 1.5 seconds until status is `completed`
- **UI sections**:
  - Header with scan form (repo URL, branch, scan button)
  - Readiness score card with executive summary
  - Hotspot heatmap (grid of clickable cards)
  - Phased roadmap (3 columns: now, next, later)
  - Slide-out panel for hotspot details and handoff pack preview
- **Styling**: Tailwind CSS with dark theme (slate color palette)

---

## Key Design Decisions

### 1. Deterministic Detectors Are the Source of Truth

**Why**: Detectors analyze code structure, dependencies, and metadata using static analysis. They produce consistent, reproducible results that don't depend on LLM availability or prompt engineering.

**Implication**: The Radar can always return a valid scan result, even if watsonx.ai is down. Hotspots are identified by detectors; the LLM only adds narrative polish.

### 2. watsonx.ai Is Additive with WatsonxUnavailable Fallback

**Why**: LLM-generated narratives improve readability and context, but they're not essential for the core functionality. If watsonx.ai is unavailable (missing `WATSONX_API_KEY`, network timeout, API error), the app logs a warning and returns deterministic results without narratives.

**Implementation**:
- [`llm.py`](apps/api/llm.py) raises `WatsonxUnavailable` exception on any failure
- [`runner.py`](apps/api/scanners/runner.py) catches this exception and logs it, but continues with the scan
- [`main.py`](apps/api/

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
Tool [write_to_file] was not executed because a tool has already been used in this message. Only one tool may be used per message. You must assess the first tool's result before proceeding to use the next tool.
<environment_details>
# VSCode Visible Files


# VSCode Open Tabs


# Current Time
Current time in ISO 8601 UTC format: 2026-05-03T01:17:34.111Z
User time zone: Africa/Tunis, UTC+1:00

# Current Cost
$0.20

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Read project files to understand architecture and implementation | Completed |
| 2 | Gather information about scanner detectors and LLM integration | Completed |
| 3 | Review deployment configuration and environment variables | Completed |
| 4 | Create comprehensive AGENTS.md file with all required sections | In Progress |
| 5 | Review and validate the documentation | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

Now I'll create the comprehensive AGENTS.md file:

<write_to_file>
<path>AGENTS.md</path>
<content># Legacy Modernization Radar — Agent Documentation

## Project Overview

**Legacy Modernization Radar** is a control-tower web application built for the IBM Bob Dev Day Hackathon (May 1-3, 2026). It scans legacy repositories, ranks modernization hotspots by severity and category, and generates a structured handoff pack for IBM Bob to execute one approved fix with passing tests.

### Target Users
Engineering leaders and technical staff who need to prioritize modernization work across legacy codebases without manually auditing every file.

### Key User Flow
1. **Paste repository URL** → User enters a GitHub repository URL and branch name in the web UI
2. **See scan results** → The Radar clones the repo, runs deterministic detectors, enriches findings with watsonx.ai narratives, and displays:
   - Readiness score (0-100)
   - Hotspot heatmap (categorized by severity: Critical, High, Medium, Low)
   - Phased roadmap (now, next, later workstreams)
   - Executive summary
3. **Click hotspot** → User selects a hotspot to view details, affected files, and recommended action
4. **Preview Bob handoff pack** → User sees the structured prompt, target files, acceptance criteria, and test plan that will be sent to IBM Bob
5. **Approve** → User approves the hotspot, signaling readiness to hand off to Bob for execution

---

## Architecture

### Monorepo Layout

```
Legacy-Modernization-Radar/
├── apps/
│   ├── api/              # FastAPI backend (Python 3.11)
│   │   ├── main.py       # FastAPI app, endpoints, in-memory scan cache
│   │   ├── schema.py     # Pydantic models (source of truth for types)
│   │   ├── llm.py        # watsonx.ai integration with fallback handling
│   │   ├── scanners/     # Detector pipeline
│   │   │   ├── __init__.py
│   │   │   ├── runner.py          # Orchestrates detectors, groups workstreams
│   │   │   ├── clone.py           # Shallow git clone utility
│   │   │   ├── dependency_cve.py  # CVE detector (placeholder)
│   │   │   ├── test_coverage.py   # Test coverage detector (placeholder)
│   │   │   └── complex_methods.py # Cyclomatic complexity detector (placeholder)
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── fly.toml      # Fly.io deployment config
│   └── web/              # Vite + React + TypeScript + Tailwind frontend
│       ├── src/
│       │   ├── App.tsx   # Main UI component (scan form, heatmap, roadmap, handoff preview)
│       │   ├── lib/
│       │   │   └── types.ts  # TypeScript types mirroring schema.py
│       │   ├── main.tsx
│       │   └── index.css
│       ├── package.json
│       ├── Dockerfile
│       └── .env.production  # VITE_API_URL for Vercel deploy
├── docker-compose.yml
└── README.md
```

### Communication Between API and Web

- **API** exposes REST endpoints at `http://localhost:8080` (dev) or `https://legacy-radar-api.fly.dev` (prod)
- **Web** polls the API for scan results every 1.5 seconds until status is `completed`
- **No websockets** — polling is simpler for a hackathon demo and avoids connection management complexity
- **CORS** is configured in [`apps/api/main.py`](apps/api/main.py:85-91) via `CORS_ORIGINS` environment variable

### Key Modules

#### Scanner Detector Pipeline ([`apps/api/scanners/`](apps/api/scanners/))

- **[`runner.py`](apps/api/scanners/runner.py)**: Orchestrates the scan lifecycle
  - Clones the repository using [`clone.py`](apps/api/scanners/clone.py)
  - Runs all detectors in sequence: `scan_dependencies`, `scan_test_coverage`, `scan_complex_methods` ([`runner.py:124-131`](apps/api/scanners/runner.py:124-131))
  - Deduplicates hotspots by ID ([`runner.py:134-138`](apps/api/scanners/runner.py:134-138))
  - Sorts hotspots by severity (Critical → High → Medium → Low) ([`__init__.py:18-26`](apps/api/scanners/__init__.py:18-26))
  - Calculates readiness score (100 minus severity penalties) ([`runner.py:93-97`](apps/api/scanners/runner.py:93-97))
  - Groups hotspots into workstreams by phase (now, next, later) ([`runner.py:100-121`](apps/api/scanners/runner.py:100-121))
  - Calls `enrich_with_narratives()` to add watsonx.ai-generated text ([`runner.py:82-88`](apps/api/scanners/runner.py:82-88))
  - Returns a `ScanResult` object

- **[`__init__.py`](apps/api/scanners/__init__.py)**: Utility functions
  - `make_hotspot_id()`: Generates deterministic IDs from category and title using SHA-1 hash ([`__init__.py:13-15`](apps/api/scanners/__init__.py:13-15))
  - `sort_hotspots()`: Sorts by severity order, then title, then ID ([`__init__.py:18-26`](apps/api/scanners/__init__.py:18-26))

- **Detectors** ([`dependency_cve.py`](apps/api/scanners/dependency_cve.py), [`test_coverage.py`](apps/api/scanners/test_coverage.py), [`complex_methods.py`](apps/api/scanners/complex_methods.py)):
  - Each detector scans the cloned repository and returns a list of `Hotspot` objects
  - Detectors are **deterministic** — they analyze code structure, dependencies, and metadata without LLM inference
  - Currently placeholder implementations for hackathon demo

#### watsonx.ai Narrative Integration ([`apps/api/llm.py`](apps/api/llm.py))

- **Purpose**: Enrich scan results with human-readable narratives generated by IBM Granite models
- **Key functions**:
  - `initialize_watsonx_client()`: Validates configuration on startup ([`llm.py:86-94`](apps/api/llm.py:86-94))
  - `get_iam_token()`: Fetches and caches IBM Cloud IAM token (refreshes 5 minutes before expiration) ([`llm.py:97-147`](apps/api/llm.py:97-147))
  - `generate_text()`: Calls watsonx.ai text generation API with greedy decoding ([`llm.py:150-202`](apps/api/llm.py:150-202))
  - `enrich_with_narratives()`: Generates executive summary, hotspot narratives, and workstream rationales ([`llm.py:347-380`](apps/api/llm.py:347-380))
- **Fallback behavior**: If watsonx.ai is unavailable (missing credentials, network error, timeout), the app logs a warning and returns deterministic results without narratives. **The demo never breaks.**

#### Schema ([`apps/api/schema.py`](apps/api/schema.py) ↔ [`apps/web/src/lib/types.ts`](apps/web/src/lib/types.ts))

- **Pydantic models** in `schema.py` define the API contract:
  - `Hotspot`: A single modernization issue (id, title, severity, category, summary, affected_files, recommended_action, optional CVE fields, optional narrative) ([`schema.py:11-21`](apps/api/schema.py:11-21))
  - `Workstream`: A group of hotspots in a phase (now/next/later) with effort estimate and impact description ([`schema.py:24-29`](apps/api/schema.py:24-29))
  - `ScanResult`: Complete scan output (scan_id, repo_url, branch, readiness_score, hotspots, workstreams, optional executive_summary) ([`schema.py:43-52`](apps/api/schema.py:43-52))
  - `HandoffPack`: Structured prompt for IBM Bob (hotspot_id, title, prompt, target_files, acceptance_criteria, test_plan) ([`schema.py:59-65`](apps/api/schema.py:59-65))
- **TypeScript types** in `types.ts` mirror these models exactly ([`types.ts:1-46`](apps/web/src/lib/types.ts:1-46))
- **Manual sync required** — changes to `schema.py` must be manually reflected in `types.ts`

#### Main UI Component ([`apps/web/src/App.tsx`](apps/web/src/App.tsx))

- **Single-page React app** with no routing
- **State management**: React hooks (`useState`, `useEffect`)
- **Polling logic**: `useEffect` hook polls `/api/scans/{scan_id}` every 1.5 seconds until status is `completed` ([`App.tsx:51-93`](apps/web/src/App.tsx:51-93))
- **UI sections**:
  - Header with scan form (repo URL, branch, scan button) ([`App.tsx:208-277`](apps/web/src/App.tsx:208-277))
  - Readiness score card with executive summary ([`App.tsx:280-311`](apps/web/src/App.tsx:280-311))
  - Hotspot heatmap (grid of clickable cards) ([`App.tsx:313-384`](apps/web/src/App.tsx:313-384))
  - Phased roadmap (3 columns: now, next, later) ([`App.tsx:386-408`](apps/web/src/App.tsx:386-408))
  - Slide-out panel for hotspot details and handoff pack preview ([`App.tsx:419-563`](apps/web/src/App.tsx:419-563))
- **Styling**: Tailwind CSS with dark theme (slate color palette)

---

## Key Design Decisions

### 1. Deterministic Detectors Are the Source of Truth

**Why**: Detectors analyze code structure, dependencies, and metadata using static analysis. They produce consistent, reproducible results that don't depend on LLM availability or prompt engineering.

**Implication**: The Radar can always return a valid scan result, even if watsonx.ai is down. Hotspots are identified by detectors; the LLM only adds narrative polish.

### 2. watsonx.ai Is Additive with WatsonxUnavailable Fallback

**Why**: LLM-generated narratives improve readability and context, but they're not essential for the core functionality. If watsonx.ai is unavailable (missing `WATSONX_API_KEY`, network timeout, API error), the app logs a warning and returns deterministic results without narratives.

**Implementation**:
- [`llm.py`](apps/api/llm.py:82-83) raises `WatsonxUnavailable` exception on any failure
- [`runner.py`](apps/api/scanners/runner.py:82-88) catches this exception and logs it, but continues with the scan
- [`main.py`](apps/api/main.py:69-78) attempts to initialize the watsonx client on startup but doesn't fail if unavailable
- **Result**: The demo never breaks, even without watsonx.ai credentials

### 3. Forced-Sentence-Starter Prompts + Post-Hoc Sanitizer for IBM Granite

**Why**: IBM Granite models (especially `ibm/granite-3-8b-instruct`) tend to generate verbose, jargon-heavy text with phrases like "modernization posture", "engineering risk", "leverage", etc. These phrases are banned because they sound like corporate buzzwords rather than actionable engineering guidance.

**Implementation**:
- **Forced sentence starters**: Prompts explicitly require sentences to start with specific words (e.g., "Sentence 1 MUST start with 'The repository scores'") ([`llm.py:292`](apps/api/llm.py:292))
- **Banned phrases list**: 18 phrases explicitly forbidden in prompts ([`llm.py:29-49`](apps/api/llm.py:29-49))
- **Post-hoc sanitizer**: After generation, a regex-based sanitizer replaces banned phrases with neutral alternatives ([`llm.py:54-75`](apps/api/llm.py:54-75), [`llm.py:431-438`](apps/api/llm.py:431-438))
- **Sentence limiting**: Responses are truncated to the requested number of sentences to prevent rambling ([`llm.py:441-449`](apps/api/llm.py:441-449))

**Example**: "modernization posture" → "state", "leverage" → "use", "robust" → "reliable"

### 4. Scan Results Cached In-Memory Keyed by scan_id

**Why**: For a hackathon demo, in-memory caching is the simplest approach. No database setup, no persistence layer, no serialization complexity.

**Implementation**:
- [`main.py:32`](apps/api/main.py:32) defines `SCAN_RESULTS: dict[str, ScanResult] = {}`
- [`main.py:123`](apps/api/main.py:123) stores scan results after completion
- [`main.py:129`](apps/api/main.py:129) retrieves scan results by `scan_id`

**Tradeoff**: Scan results are lost on server restart. For production, this would need a database (PostgreSQL, Redis, etc.).

### 5. Frontend Polls Instead of Using Websockets

**Why**: Polling is simpler to implement and debug for a hackathon demo. No need to manage websocket connections, reconnection logic, or server-side event broadcasting.

**Implementation**:
- [`App.tsx:51-93`](apps/web/src/App.tsx:51-93) uses a `useEffect` hook with a 1.5-second polling interval
- Polling stops when `result.status === 'completed'`
- Cleanup function cancels pending timeouts on unmount

**Tradeoff**: Slightly higher latency and server load compared to websockets, but negligible for a demo with low traffic.

---

## Build and Run

### Local Development

#### Native Development (Recommended for Active Development)

**API terminal:**
```bash
cd apps/api
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn main:app --port 8080
```

**Web terminal:**
```bash
cd apps/web
npm install
npm run dev
```

**Ports:**
- Vite dev server: `http://localhost:5173`
- FastAPI: `http://localhost:8080`
- Health check: `http://localhost:8080/health`

**Environment variables:**
- Create `apps/api/.env` with watsonx.ai credentials (see Configuration Surface below)
- Set `VITE_API_URL=http://localhost:8080` if needed (defaults to `http://localhost:8080`)

#### Docker Compose (Full-Stack Local)

From the repo root:
```bash
docker compose up --build
```

**Ports:**
- Web UI: `http://localhost:8081`
- API: `http://localhost:8080`
- Health check: `http://localhost:8080/health`

**Note**: The web build bakes `VITE_API_URL=http://localhost:8080` via [`docker-compose.yml:14-15`](docker-compose.yml:14-15), so the browser talks to the API on port 8080 while the UI is served on port 8081.

### Production Deployment

#### API: Fly.io

**Configuration**: [`apps/api/fly.toml`](apps/api/fly.toml)
- App name: `legacy-radar-api`
- Region: `iad` (US East)
- Dockerfile: [`apps/api/Dockerfile`](apps/api/Dockerfile)
- Health check: `GET /health` every 30 seconds
- Auto-stop/start machines enabled (min 0 machines running)

**Deploy:**
```bash
cd apps/api
fly deploy
```

**Set secrets:**
```bash
fly secrets set WATSONX_API_KEY=your_key_here
fly secrets set WATSONX_PROJECT_ID=your_project_id_here
```

**Environment variables** (set in [`fly.toml`](apps/api/fly.toml:12-14)):
- `PORT=8080`
- `CORS_ORIGINS=*`

#### Web: Vercel

**Configuration**: [`apps/web/.env.production`](apps/web/.env.production)
- `VITE_API_URL=https://legacy-radar-api.fly.dev`

**Deploy:**
```bash
cd apps/web
vercel --prod
```

**Note**: Vercel automatically detects Vite projects and builds them. The `VITE_API_URL` is baked into the build at deploy time.

---

## Configuration Surface

### Environment Variables

#### API ([`apps/api/main.py`](apps/api/main.py), [`apps/api/llm.py`](apps/api/llm.py))

| Variable | Type | Required | Default | Description | Where Set |
|----------|------|----------|---------|-------------|-----------|
| `WATSONX_API_KEY` | Secret | No* | — | IBM Cloud API key for watsonx.ai authentication | `apps/api/.env` (dev), Fly.io secrets (prod) |
| `WATSONX_PROJECT_ID` | Secret | No* | — | watsonx.ai project ID | `apps/api/.env` (dev), Fly.io secrets (prod) |
| `WATSONX_URL` | Public | No | `https://us-south.ml.cloud.ibm.com` | watsonx.ai API base URL | `apps/api/.env` (dev), Fly.io env (prod) |
| `WATSONX_MODEL_ID` | Public | No | `ibm/granite-3-8b-instruct` | watsonx.ai model ID | `apps/api/.env` (dev), Fly.io env (prod) |
| `PORT` | Public | No | `8080` | Port for FastAPI server | `apps/api/.env` (dev), [`fly.toml`](apps/api/fly.toml:14) (prod) |
| `CORS_ORIGINS` | Public | No | `*` | Comma-separated list of allowed CORS origins | `apps/api/.env` (dev), [`fly.toml`](apps/api/fly.toml:13) (prod) |

**\*Note**: `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are not strictly required because the app falls back to deterministic results if watsonx.ai is unavailable. However, narratives will be missing without these credentials.

#### Web ([`apps/web/src/App.tsx`](apps/web/src/App.tsx))

| Variable | Type | Required | Default | Description | Where Set |
|----------|------|----------|---------|-------------|-----------|
| `VITE_API_URL` | Public | No | `http://localhost:8080` | API base URL | `apps/web/.env.production` (prod), CLI arg (dev) |

**Note**: `VITE_API_URL` is baked into the build at compile time. It's not a runtime environment variable.

### .env Files

- **`apps/api/.env`**: Gitignored, never committed. Contains watsonx.ai secrets for local development.
- **`apps/web/.env.production`**: Committed to the repo. Contains public `VITE_API_URL` for Vercel deployment.

**Example `apps/api/.env`:**
```bash
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
PORT=8080
CORS_ORIGINS=http://localhost:5173,http://localhost:8081,*
```

---

## Test Surface

### What's Currently Tested

**Nothing.** This is a hackathon prototype with zero automated tests.

### What Isn't Tested

- **Detector logic**: No unit tests for `scan_dependencies`, `scan_test_coverage`, `scan_complex_methods`
- **Scanner orchestration**: No tests for `run_scan`, `calculate_readiness`, `group_into_workstreams`
- **LLM integration**: No tests for `generate_text`, `enrich_with_narratives`, prompt construction, or sanitization
- **API endpoints**: No integration tests for `/api/scans`, `/api/hotspots/{id}/approve`, `/api/hotspots/{id}/handoff`
- **Frontend components**: No React component tests, no end-to-end tests

### Gaps Bob Would Prioritize First

If asked to add test coverage, Bob should prioritize in this order:

1. **Detector unit tests** ([`apps/api/scanners/`](apps/api/scanners/))
   - Test each detector with known-good and known-bad inputs
   - Verify hotspot IDs are deterministic
   - Verify severity assignments are correct
   - **Why first**: Detectors are the source of truth; bugs here corrupt all downstream results

2. **Scanner orchestration tests** ([`apps/api/scanners/runner.py`](apps/api/scanners/runner.py))
   - Test `calculate_readiness` with various hotspot combinations
   - Test `group_into_workstreams` phase assignment logic
   - Test deduplication and sorting
   - **Why second**: Orchestration bugs affect the entire scan result

3. **API endpoint integration tests** ([`apps/api/main.py`](apps/api/main.py))
   - Test `/api/scans` POST → GET flow
   - Test `/api/hotspots/{id}/approve` and `/api/hotspots/{id}/handoff`
   - Test error cases (404, invalid input)
   - **Why third**: Ensures the API contract is stable

4. **LLM sanitization tests** ([`apps/api/llm.py`](apps/api/llm.py))
   - Test `_sanitize` with known banned phrases
   - Test `_limit_sentences` with various inputs
   - Test `_extract_answer` with malformed XML
   - **Why fourth**: Sanitization is critical for output quality, but LLM failures don't break the app

5. **Frontend component tests** ([`apps/web/src/App.tsx`](apps/web/src/App.tsx))
   - Test polling logic with mocked API responses
   - Test hotspot selection and handoff pack loading
   - Test error handling
   - **Why last**: Frontend bugs are visible and easy to debug manually

---

## Notable Conventions

### TypeScript Types Mirror Pydantic Models

- **Source of truth**: [`apps/api/schema.py`](apps/api/schema.py)
- **Mirror**: [`apps/web/src/lib/types.ts`](apps/web/src/lib/types.ts)
- **Sync**: Manual. Changes to `schema.py` must be manually reflected in `types.ts`.
- **Validation**: TypeScript compiler catches type mismatches at build time.

**Example**:
```python
# apps/api/schema.py
class Hotspot(BaseModel):
    id: str
    title: str
    severity: Severity
    # ...
```

```typescript
// apps/web/src/lib/types.ts
export interface Hotspot {
  id: string
  title: string
  severity: Severity
  // ...
}
```

### Production-Ready Dockerfiles

- **API Dockerfile** ([`apps/api/Dockerfile`](apps/api/Dockerfile)):
  - Multi-stage build (builder + runtime)
  - Python 3.11 slim base image
  - Virtual environment in `/opt/venv`
  - Non-root user (`app`)
  - Git and CA certificates installed for cloning repos
  - Health check via Python `urllib.request`

- **Web Dockerfile** ([`apps/web/Dockerfile`](apps/web/Dockerfile)):
  - Multi-stage build (build + runtime)
  - Node 20 Alpine for build, Nginx Alpine for runtime
  - `VITE_API_URL` baked in at build time via ARG
  - Nginx serves static files from `/usr/share/nginx/html`
  - Port 8080 (configurable via `PORT` env var)

### .env Files Are Gitignored

- **`apps/api/.env`**: Gitignored via [`apps/api/.gitignore`](apps/api/.gitignore) (not shown, but standard practice)
- **`apps/web/.env.production`**: Committed because it contains only public `VITE_API_URL`
- **Root `.gitignore`**: Excludes `.env` files globally

**Never commit secrets to the repo.** Use Fly.io secrets or Vercel environment variables for production.

---

## Quick Reference

### Key Files

| File | Purpose |
|------|---------|
| [`apps/api/main.py`](apps/api/main.py) | FastAPI app, endpoints, in-memory scan cache |
| [`apps/api/schema.py`](apps/api/schema.py) | Pydantic models (API contract) |
| [`apps/api/llm.py`](apps/api/llm.py) | watsonx.ai integration with fallback |
| [`apps/api/scanners/runner.py`](apps/api/scanners/runner.py) | Scan orchestration |
| [`apps/api/scanners/__init__.py`](apps/api/scanners/__init__.py) | Hotspot ID generation and sorting |
| [`apps/web/src/App.tsx`](apps/web/src/App.tsx) | Main UI component |
| [`apps/web/src/lib/types.ts`](apps/web/src/lib/types.ts) | TypeScript types (mirrors schema.py) |
| [`docker-compose.yml`](docker-compose.yml) | Local full-stack development |
| [`apps/api/fly.toml`](apps/api/fly.toml) | Fly.io deployment config |
| [`apps/web/.env.production`](apps/web/.env.production) | Vercel deployment config |

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check (returns `{"ok": true}`) |
| `GET` | `/api/llm/health` | watsonx.ai availability check |
| `POST` | `/api/scans` | Create a new scan (returns `scan_id`) |
| `GET` | `/api/scans/{scan_id}` | Get scan result (poll until `status: "completed"`) |
| `POST` | `/api/hotspots/{hotspot_id}/approve` | Approve a hotspot (returns `{"ok": true}`) |
| `POST` | `/api/hotspots/{hotspot_id}/handoff` | Get handoff pack for a hotspot |

### Severity Penalties (Readiness Score)

| Severity | Penalty |
|----------|---------|
| Critical | -25 |
| High | -15 |
| Medium | -5 |
| Low | -1 |

**Formula**: `readiness_score = max(100 - sum(penalties), 0)`

### Phase Assignment (Workstreams)

| Severity | Phase |
|----------|-------|
| Critical | now |
| High | next |
| Medium | later |
| Low | later |

---

## Troubleshooting

### "watsonx.ai unavailable" in logs

**Cause**: Missing `WATSONX_API_KEY` or `WATSONX_PROJECT_ID`, or network error.

**Fix**: Set credentials in `apps/api/.env` (dev) or Fly.io secrets (prod). The app will continue to work without narratives.

### Scan results disappear after server restart

**Cause**: Scan results are cached in-memory ([`main.py:32`](apps/api/main.py:32)).

**Fix**: For production, implement persistent storage (PostgreSQL, Redis, etc.).

### Frontend shows "Request failed with status 404"

**Cause**: `scan_id` not found in `SCAN_RESULTS` cache.

**Fix**: Ensure the scan was created successfully. Check API logs for errors during scan creation.

### Polling never stops

**Cause**: Scan status never reaches `"completed"`.

**Fix**: Check API logs for errors in `run_scan`. Ensure detectors are not throwing unhandled exceptions.

### Narratives contain banned phrases

**Cause**: Sanitizer regex patterns may not cover all variations.

**Fix**: Add new patterns to `SANITIZE_REPLACEMENTS` in [`llm.py:54-75`](apps/api/llm.py:54-75).

---

## Future Enhancements

If this project were to continue beyond the hackathon, consider:

1. **Persistent storage**: Replace in-memory cache with PostgreSQL or Redis
2. **Real detectors**: Implement actual CVE scanning, test coverage analysis, and cyclomatic complexity detection
3. **Websockets**: Replace polling with real-time updates
4. **Authentication**: Add user accounts and API keys
5. **Test coverage**: Add unit tests, integration tests, and end-to-end tests
6. **CI/CD**: Automate deployment with GitHub Actions
7. **Monitoring**: Add logging, metrics, and error tracking (Sentry, Datadog, etc.)
8. **Rate limiting**: Protect API endpoints from abuse
9. **Caching**: Cache LLM responses to reduce API costs
10. **Multi-repo support**: Allow users to scan multiple repositories and compare results

---

**Built for IBM Bob Dev Day Hackathon, May 1-3, 2026.**
</content>
<line_count>549</line_count>
</write_to_file>

---

**User:**

[write_to_file for 'AGENTS.md'] Result:
<file_write_result>
<path>AGENTS.md</path>
<operation>created</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<environment_details>
# VSCode Visible Files
AGENTS.md

# VSCode Open Tabs
AGENTS.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-03T01:19:16.489Z
User time zone: Africa/Tunis, UTC+1:00

# Current Cost
$0.32

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Read project files to understand architecture and implementation | Completed |
| 2 | Gather information about scanner detectors and LLM integration | Completed |
| 3 | Review deployment configuration and environment variables | Completed |
| 4 | Create comprehensive AGENTS.md file with all required sections | In Progress |
| 5 | Review and validate the documentation | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<update_todo_list>
<todos>
[x] Read project files to understand architecture and implementation
[x] Gather information about scanner detectors and LLM integration
[x] Review deployment configuration and environment variables
[x] Create comprehensive AGENTS.md file with all required sections
[-] Review and validate the documentation
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
AGENTS.md

# VSCode Open Tabs
AGENTS.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-03T01:19:26.250Z
User time zone: Africa/Tunis, UTC+1:00

# Current Cost
$0.47

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Read project files to understand architecture and implementation | Completed |
| 2 | Gather information about scanner detectors and LLM integration | Completed |
| 3 | Review deployment configuration and environment variables | Completed |
| 4 | Create comprehensive AGENTS.md file with all required sections | Completed |
| 5 | Review and validate the documentation | In Progress |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
Created comprehensive AGENTS.md documentation at the repo root with:

**Project Overview**: Control-tower web app for scanning legacy repos, ranking modernization hotspots, and generating IBM Bob handoff packs

**Architecture**: Detailed monorepo layout showing FastAPI backend (Python 3.11) and Vite + React + TypeScript frontend, with specific file paths and module descriptions

**Key Design Decisions**:
- Deterministic detectors as source of truth
- watsonx.ai additive with WatsonxUnavailable fallback
- Forced-sentence-starter prompts + post-hoc sanitizer for IBM Granite
- In-memory scan cache keyed by scan_id
- Frontend polling instead of websockets

**Build and Run**: Native development commands, Docker Compose setup, and production deployment instructions for Fly.io (API) and Vercel (web)

**Configuration Surface**: Complete environment variable table with types, defaults, and where they're set in dev vs production

**Test Surface**: Current state (zero tests), what's missing, and Bob's prioritization order for adding coverage

**Notable Conventions**: TypeScript types mirror Pydantic models, production-ready Dockerfiles, gitignored .env files

**Quick Reference**: Key files table, API endpoints, severity penalties, phase assignments, troubleshooting guide, and future enhancements
</result>
</attempt_completion>

