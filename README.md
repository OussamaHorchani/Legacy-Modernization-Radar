# Legacy Modernization Radar

Built for the IBM Bob Dev Day Hackathon, May 1-3, 2026.

A control-tower web app that scans legacy codebases, ranks modernization hotspots, and hands one approved fix to IBM Bob to execute with passing tests.

## Local development

### Docker Compose

From the repo root, build and run both services:

```bash
docker compose up --build
```

- Web UI: `http://localhost:8081`
- API: `http://localhost:8080`
- Health check: `curl http://localhost:8080/health`

The web build bakes `VITE_API_URL=http://localhost:8080`, so the browser talks to the API on port `8080` while the UI is served on port `8081`.

### Native development

API terminal:

```bash
cd apps/api
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn main:app --port 8080
```

Web terminal:

```bash
cd apps/web
npm install
npm run dev
```

Ports:

- Vite dev server: `http://localhost:5173`
- FastAPI: `http://localhost:8080`
- Health check: `http://localhost:8080/health`

If you need to point the web app at a different backend, start Vite with `VITE_API_URL=http://localhost:8080 npm run dev`.
