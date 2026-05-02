import os
from contextlib import asynccontextmanager
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schema import (
    ApproveResponse,
    HandoffPack,
    Hotspot,
    ScanCreateRequest,
    ScanCreateResponse,
    ScanResult,
    Workstream,
)

PORT = int(os.getenv("PORT", "8080"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]
SCAN_RESULTS: dict[str, ScanResult] = {}


def build_hotspots() -> list[Hotspot]:
    return [
        Hotspot(
            id="hotspot-cve-commons-collections",
            title="Critical CVE in commons-collections:3.2.1",
            severity="Critical",
            category="runtime",
            summary=(
                "A vulnerable transitive dependency is still pinned to "
                "commons-collections:3.2.1. The package is associated with known "
                "remote code execution gadget chains and carries a CVSS 9.8 risk."
            ),
            affected_files=["pom.xml"],
            recommended_action=(
                "Upgrade or exclude commons-collections:3.2.1, verify the resolved "
                "dependency tree, and rerun the application smoke tests."
            ),
        ),
        Hotspot(
            id="hotspot-search-owners-with-filters",
            title="Untested method: searchOwnersWithFilters",
            severity="High",
            category="architecture",
            summary=(
                "The owner search path branches across multiple optional filters, "
                "but the core searchOwnersWithFilters method has no focused test "
                "coverage for mixed criteria or empty-result behavior."
            ),
            affected_files=[
                "src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java",
                "src/main/java/org/springframework/samples/petclinic/owner/OwnerService.java",
            ],
            recommended_action=(
                "Add targeted tests around the searchOwnersWithFilters query contract "
                "before refactoring the search flow or adding more filter branches."
            ),
        ),
        Hotspot(
            id="hotspot-owner-controller-tests",
            title="Missing tests in OwnerController",
            severity="Medium",
            category="quality",
            summary=(
                "OwnerController handles validation and search orchestration, but "
                "key request flows are not covered by controller-level tests. That "
                "raises regression risk when routing or binding behavior changes."
            ),
            affected_files=[
                "src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java",
                "src/test/java/org/springframework/samples/petclinic/owner/OwnerControllerTests.java",
            ],
            recommended_action=(
                "Backfill controller tests for the main GET/POST owner flows and "
                "validation edge cases before shipping broader modernization work."
            ),
        ),
    ]


def build_workstreams() -> list[Workstream]:
    return [
        Workstream(
            phase="now",
            hotspot_ids=["hotspot-cve-commons-collections"],
            effort="0.5-1 day",
            impact="Removes the most urgent supply-chain risk before any further rollout.",
        ),
        Workstream(
            phase="next",
            hotspot_ids=["hotspot-search-owners-with-filters"],
            effort="1-2 days",
            impact="Stabilizes the highest-risk business query path with focused coverage.",
        ),
        Workstream(
            phase="later",
            hotspot_ids=["hotspot-owner-controller-tests"],
            effort="1 day",
            impact="Improves regression confidence around the owner entry points.",
        ),
    ]


def build_scan_result(scan_id: str, request: ScanCreateRequest) -> ScanResult:
    return ScanResult(
        scan_id=scan_id,
        repo_url=request.repo_url,
        branch=request.branch,
        scenario_id=request.scenario_id,
        readiness_score=62,
        hotspots=build_hotspots(),
        workstreams=build_workstreams(),
    )


def build_handoff_pack(hotspot_id: str) -> HandoffPack:
    if hotspot_id == "hotspot-cve-commons-collections":
        return HandoffPack(
            hotspot_id=hotspot_id,
            title="Upgrade vulnerable commons-collections dependency",
            prompt=(
                "Update the Maven dependency graph so commons-collections:3.2.1 is "
                "no longer resolved. Prefer a direct upgrade or a safe exclusion on "
                "the parent dependency, then confirm the application still builds and "
                "the owner flows keep working."
            ),
            target_files=["pom.xml"],
            acceptance_criteria=[
                "The build no longer resolves commons-collections:3.2.1.",
                "Any replacement version or exclusion is documented inline in pom.xml.",
                "The application test suite still passes after the dependency change.",
            ],
            test_plan=[
                "Run `mvn -q dependency:tree` and confirm the vulnerable artifact is gone.",
                "Run `mvn test` to catch compatibility regressions.",
                "Smoke-test the owner search flow manually after the build succeeds.",
            ],
        )

    if hotspot_id == "hotspot-search-owners-with-filters":
        return HandoffPack(
            hotspot_id=hotspot_id,
            title="Add focused coverage for searchOwnersWithFilters",
            prompt=(
                "Create a focused test harness around searchOwnersWithFilters so mixed "
                "criteria, empty matches, and single-filter cases are covered before "
                "we touch the implementation. Keep the existing method contract intact."
            ),
            target_files=[
                "src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java",
                "src/main/java/org/springframework/samples/petclinic/owner/OwnerService.java",
                "src/test/java/org/springframework/samples/petclinic/owner/OwnerRepositoryTests.java",
            ],
            acceptance_criteria=[
                "Tests cover mixed filters, empty results, and happy-path matches.",
                "The current method signature and public behavior remain unchanged.",
                "The new tests fail if the search logic regresses on optional filters.",
            ],
            test_plan=[
                "Run the owner repository or service test slice locally.",
                "Verify at least one empty-result assertion and one multi-filter assertion.",
                "Run the broader owner-related test suite to confirm no contract drift.",
            ],
        )

    if hotspot_id == "hotspot-owner-controller-tests":
        return HandoffPack(
            hotspot_id=hotspot_id,
            title="Backfill OwnerController request-flow tests",
            prompt=(
                "Add controller-level tests for OwnerController covering the main owner "
                "search and create flows, plus validation failures. Keep the controller "
                "behavior unchanged and focus on raising confidence around routing and "
                "binding edge cases."
            ),
            target_files=[
                "src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java",
                "src/test/java/org/springframework/samples/petclinic/owner/OwnerControllerTests.java",
            ],
            acceptance_criteria=[
                "Search and create endpoints are both covered by controller tests.",
                "At least one validation failure case is asserted explicitly.",
                "The new tests are readable enough to serve as guardrails for future edits.",
            ],
            test_plan=[
                "Run the controller test class in isolation while iterating.",
                "Run the full owner-related test package once the new cases pass.",
                "Manually verify response codes and model attributes for the validation path.",
            ],
        )

    raise HTTPException(status_code=404, detail="Hotspot not found")


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Legacy Modernization Radar API starting up")
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


@app.post("/api/scans", response_model=ScanCreateResponse)
async def create_scan(request: ScanCreateRequest) -> ScanCreateResponse:
    scan_id = str(uuid4())
    SCAN_RESULTS[scan_id] = build_scan_result(scan_id, request)
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
