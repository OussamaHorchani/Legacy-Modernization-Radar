# Legacy Modernization Radar — Agent Documentation

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