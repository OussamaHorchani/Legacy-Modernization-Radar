import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from llm import WatsonxUnavailable, generate_text, initialize_watsonx_client
from scanners.runner import run_scan
from schema import (
    ApproveResponse,
    HandoffPack,
    Hotspot,
    ScanCreateRequest,
    ScanCreateResponse,
    ScanResult,
)

load_dotenv(Path(__file__).with_name(".env"))

logger = logging.getLogger("uvicorn.error")
PORT = int(os.getenv("PORT", "8080"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]
SCAN_RESULTS: dict[str, ScanResult] = {}


def build_handoff_pack(hotspot_id: str) -> HandoffPack:
    hotspot = find_hotspot(hotspot_id)
    if hotspot is None:
        raise HTTPException(status_code=404, detail="Hotspot not found")

    return HandoffPack(
        hotspot_id=hotspot.id,
        title=f"Remediate {hotspot.title}",
        prompt=(
            f"Address the hotspot titled '{hotspot.title}'. {hotspot.summary} "
            f"Recommended action: {hotspot.recommended_action}"
        ),
        target_files=hotspot.affected_files,
        acceptance_criteria=[
            "The hotspot is no longer reported by the detector after the change.",
            "The relevant production behavior remains intact after remediation.",
            "The fix is documented clearly enough for a follow-on reviewer to validate quickly.",
        ],
        test_plan=[
            "Run the smallest focused test slice that exercises the affected area.",
            "Run at least one broader regression check for the surrounding module.",
            "Re-run the Radar scan and confirm this hotspot disappears or changes severity appropriately.",
        ],
    )


def find_hotspot(hotspot_id: str) -> Hotspot | None:
    for scan_result in SCAN_RESULTS.values():
        for hotspot in scan_result.hotspots:
            if hotspot.id == hotspot_id:
                return hotspot
    return None


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Legacy Modernization Radar API starting up")
    try:
        initialize_watsonx_client()
    except WatsonxUnavailable as exc:
        logger.warning(
            "watsonx.ai client unavailable during startup",
            extra={"reason": str(exc)},
        )
    yield
    print("Legacy Modernization Radar API shutting down gracefully")


app = FastAPI(title="Legacy Modernization Radar API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, bool]:
    return {"ok": True}


@app.get("/api/llm/health")
def llm_health() -> dict[str, bool | str]:
    try:
        _ = generate_text("Say OK.", max_tokens=5)
    except WatsonxUnavailable as exc:
        return {
            "watsonx_available": False,
            "reason": str(exc),
        }

    return {"watsonx_available": True}


@app.post("/api/scans", response_model=ScanCreateResponse)
async def create_scan(request: ScanCreateRequest) -> ScanCreateResponse:
    scan_id = str(uuid4())
    scan_result = run_scan(request.repo_url, request.branch).model_copy(
        update={
            "scan_id": scan_id,
            "repo_url": request.repo_url,
            "branch": request.branch,
            "scenario_id": request.scenario_id,
        }
    )
    SCAN_RESULTS[scan_id] = scan_result
    return ScanCreateResponse(scan_id=scan_id, status="started")


@app.get("/api/scans/{scan_id}", response_model=ScanResult)
async def get_scan(scan_id: str) -> ScanResult:
    result = SCAN_RESULTS.get(scan_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return result


@app.post("/api/hotspots/{hotspot_id}/approve", response_model=ApproveResponse)
async def approve_hotspot(hotspot_id: str) -> ApproveResponse:
    _ = build_handoff_pack(hotspot_id)
    return ApproveResponse(ok=True)


@app.post("/api/hotspots/{hotspot_id}/handoff", response_model=HandoffPack)
async def handoff_hotspot(hotspot_id: str) -> HandoffPack:
    return build_handoff_pack(hotspot_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
