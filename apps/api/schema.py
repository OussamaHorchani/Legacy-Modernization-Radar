from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["Critical", "High", "Medium", "Low"]
Category = Literal["runtime", "architecture", "quality"]
Phase = Literal["now", "next", "later"]
ScanStatus = Literal["started", "completed"]


class Hotspot(BaseModel):
    id: str
    title: str
    severity: Severity
    category: Category
    summary: str
    affected_files: list[str] = Field(default_factory=list)
    recommended_action: str
    cve_id: str | None = None
    cvss_score: float | None = None
    narrative: str | None = None


class Workstream(BaseModel):
    phase: Phase
    hotspot_ids: list[str] = Field(default_factory=list)
    effort: str
    impact: str
    rationale: str | None = None


class ScanCreateRequest(BaseModel):
    repo_url: str
    branch: str
    scenario_id: str | None = None


class ScanCreateResponse(BaseModel):
    scan_id: str
    status: Literal["started"]


class ScanResult(BaseModel):
    scan_id: str
    repo_url: str
    branch: str
    scenario_id: str | None = None
    status: Literal["completed"] = "completed"
    readiness_score: int
    hotspots: list[Hotspot] = Field(default_factory=list)
    workstreams: list[Workstream] = Field(default_factory=list)
    executive_summary: str | None = None


class ApproveResponse(BaseModel):
    ok: bool = True


class HandoffPack(BaseModel):
    hotspot_id: str
    title: str
    prompt: str
    target_files: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    test_plan: list[str] = Field(default_factory=list)
