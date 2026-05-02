export type Severity = 'Critical' | 'High' | 'Medium' | 'Low'
export type HotspotCategory = 'runtime' | 'architecture' | 'quality'
export type WorkstreamPhase = 'now' | 'next' | 'later'
export type ScanStatus = 'started' | 'completed'

export interface Hotspot {
  id: string
  title: string
  severity: Severity
  category: HotspotCategory
  summary: string
  affected_files: string[]
  recommended_action: string
  cve_id?: string | null
  cvss_score?: number | null
  narrative?: string | null
}

export interface Workstream {
  phase: WorkstreamPhase
  hotspot_ids: string[]
  effort: string
  impact: string
  rationale?: string | null
}

export interface ScanResult {
  scan_id: string
  repo_url: string
  branch: string
  scenario_id: string | null
  status: ScanStatus
  readiness_score: number
  hotspots: Hotspot[]
  workstreams: Workstream[]
  executive_summary?: string | null
}

export interface HandoffPack {
  hotspot_id: string
  title: string
  prompt: string
  target_files: string[]
  acceptance_criteria: string[]
  test_plan: string[]
}
