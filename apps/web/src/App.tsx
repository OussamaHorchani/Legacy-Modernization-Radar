// /Users/oussama/dev/hackathon/Legacy-Modernization-Radar/apps/web/src/App.tsx

import { useEffect, useState } from 'react'

import type {
  HandoffPack,
  Hotspot,
  ScanResult,
  Workstream,
  WorkstreamPhase,
} from './lib/types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8080'
const DEFAULT_REPO_URL =
  'https://github.com/OussamaHorchani/spring-framework-petclinic'
const DEFAULT_BRANCH = 'legacy-baseline'
const PHASES: WorkstreamPhase[] = ['now', 'next', 'later']

type AppScanStatus = 'idle' | 'started' | 'completed'

const phaseLabels: Record<WorkstreamPhase, string> = {
  now: 'Now',
  next: 'Next',
  later: 'Later',
}

const severityStyles: Record<Hotspot['severity'], string> = {
  Critical: 'border-red-500/60 bg-red-500/10 text-red-100',
  High: 'border-orange-500/60 bg-orange-500/10 text-orange-100',
  Medium: 'border-amber-500/60 bg-amber-500/10 text-amber-100',
  Low: 'border-emerald-500/60 bg-emerald-500/10 text-emerald-100',
}

function App() {
  const [repoUrl, setRepoUrl] = useState(DEFAULT_REPO_URL)
  const [branch, setBranch] = useState(DEFAULT_BRANCH)
  const [scanId, setScanId] = useState<string | null>(null)
  const [scanStatus, setScanStatus] = useState<AppScanStatus>('idle')
  const [scanResult, setScanResult] = useState<ScanResult | null>(null)
  const [selectedHotspotId, setSelectedHotspotId] = useState<string | null>(null)
  const [handoffPack, setHandoffPack] = useState<HandoffPack | null>(null)
  const [isScanning, setIsScanning] = useState(false)
  const [isHandoffLoading, setIsHandoffLoading] = useState(false)
  const [isApproving, setIsApproving] = useState(false)
  const [approvedHotspotIds, setApprovedHotspotIds] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)

  const selectedHotspot =
    scanResult?.hotspots.find((hotspot) => hotspot.id === selectedHotspotId) ?? null

  useEffect(() => {
    if (!scanId) {
      return
    }

    let cancelled = false
    let timeoutId: number | undefined

    const pollScan = async () => {
      try {
        const result = await fetchJson<ScanResult>(`${API_URL}/api/scans/${scanId}`)
        if (cancelled) {
          return
        }

        setScanResult(result)
        setScanStatus(result.status)
        setIsScanning(false)
        setError(null)

        if (result.status !== 'completed') {
          timeoutId = window.setTimeout(pollScan, 1500)
        }
      } catch (pollError) {
        if (cancelled) {
          return
        }

        setError(getErrorMessage(pollError))
        setIsScanning(false)
        setScanStatus('idle')
      }
    }

    void pollScan()

    return () => {
      cancelled = true
      if (timeoutId) {
        window.clearTimeout(timeoutId)
      }
    }
  }, [scanId])

  useEffect(() => {
    if (!selectedHotspot) {
      setHandoffPack(null)
      return
    }

    let cancelled = false

    const loadHandoffPack = async () => {
      setIsHandoffLoading(true)

      try {
        const pack = await fetchJson<HandoffPack>(
          `${API_URL}/api/hotspots/${selectedHotspot.id}/handoff`,
          {
            method: 'POST',
          },
        )

        if (!cancelled) {
          setHandoffPack(pack)
        }
      } catch (handoffError) {
        if (!cancelled) {
          setError(getErrorMessage(handoffError))
        }
      } finally {
        if (!cancelled) {
          setIsHandoffLoading(false)
        }
      }
    }

    setHandoffPack(null)
    void loadHandoffPack()

    return () => {
      cancelled = true
    }
  }, [selectedHotspot])

  const handleScan = async () => {
    const trimmedRepoUrl = repoUrl.trim()
    const trimmedBranch = branch.trim() || 'main'
    if (!trimmedRepoUrl) {
      setError('Enter a repository URL before starting a scan.')
      return
    }

    setIsScanning(true)
    setScanStatus('started')
    setScanResult(null)
    setScanId(null)
    setSelectedHotspotId(null)
    setHandoffPack(null)
    setApprovedHotspotIds([])
    setError(null)

    try {
      const response = await fetchJson<{ scan_id: string; status: 'started' }>(
        `${API_URL}/api/scans`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            repo_url: trimmedRepoUrl,
            branch: trimmedBranch,
            scenario_id: null,
          }),
        },
      )

      setScanId(response.scan_id)
      setScanStatus(response.status)
    } catch (scanError) {
      setError(getErrorMessage(scanError))
      setIsScanning(false)
      setScanStatus('idle')
    }
  }

  const handleApprove = async () => {
    if (!selectedHotspot) {
      return
    }

    setIsApproving(true)

    try {
      await fetchJson<{ ok: true }>(
        `${API_URL}/api/hotspots/${selectedHotspot.id}/approve`,
        {
          method: 'POST',
        },
      )

      setApprovedHotspotIds((current) =>
        current.includes(selectedHotspot.id)
          ? current
          : [...current, selectedHotspot.id],
      )
    } catch (approveError) {
      setError(getErrorMessage(approveError))
    } finally {
      setIsApproving(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-6 sm:px-6 lg:px-8">
        <header className="rounded-2xl border border-slate-800 bg-slate-900/90 p-5 shadow-lg shadow-slate-950/30">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-2">
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-slate-400">
                Control Tower
              </p>
              <h1 className="text-3xl font-semibold text-white sm:text-4xl">
                Legacy Modernization Radar
              </h1>
              <p className="max-w-3xl text-sm text-slate-400 sm:text-base">
                Scan a legacy repository, rank its modernization hotspots, and
                prepare one approved handoff for IBM Bob.
              </p>
            </div>

            <div className="flex w-full flex-col gap-3 lg:max-w-3xl">
              <div className="flex flex-col gap-3 sm:flex-row">
                <label className="sr-only" htmlFor="repo-url">
                  Repository URL
                </label>
                <input
                  id="repo-url"
                  type="url"
                  value={repoUrl}
                  onChange={(event) => setRepoUrl(event.target.value)}
                  placeholder="https://github.com/org/repo"
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-500/30"
                />
                <label className="sr-only" htmlFor="branch">
                  Branch
                </label>
                <input
                  id="branch"
                  type="text"
                  value={branch}
                  onChange={(event) => setBranch(event.target.value)}
                  placeholder="branch"
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-500/30 sm:max-w-[14rem]"
                />
                <button
                  type="button"
                  onClick={handleScan}
                  disabled={isScanning}
                  className="rounded-xl bg-sky-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300"
                >
                  {isScanning ? 'Scanning...' : 'Scan'}
                </button>
              </div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-3 text-sm text-slate-400">
            <span>API: {API_URL}</span>
            <span>
              Status:{' '}
              {scanStatus === 'idle'
                ? 'Idle'
                : scanStatus === 'started'
                  ? 'Scan started'
                  : 'Scan completed'}
            </span>
            {scanId ? <span>Scan ID: {scanId}</span> : null}
          </div>

          {error ? (
            <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-100">
              {error}
            </div>
          ) : null}
        </header>

        <main className="mt-6 grid flex-1 gap-6">
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold text-white">
                  Readiness Score
                </h2>
                <p className="mt-1 text-sm text-slate-400">
                  Composite score across runtime, architecture, and quality risk.
                </p>
              </div>
              {scanResult ? (
                <p className="text-sm text-slate-400">
                  Branch <span className="font-mono text-slate-200">{scanResult.branch}</span>
                </p>
              ) : null}
            </div>

            <div className="mt-6 flex items-end gap-4">
              <div className="text-6xl font-semibold text-white sm:text-7xl">
                {scanResult?.readiness_score ?? '--'}
              </div>
              <div className="pb-2 text-sm uppercase tracking-[0.2em] text-slate-500">
                / 100
              </div>
            </div>

            {scanResult?.executive_summary ? (
              <p className="mt-5 max-w-3xl text-sm leading-7 text-slate-300">
                {scanResult.executive_summary}
              </p>
            ) : null}
          </section>

          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-white">
                  Hotspot Heatmap
                </h2>
                <p className="mt-1 text-sm text-slate-400">
                  Click a hotspot to inspect details and preview the handoff pack.
                </p>
              </div>
              {scanResult ? (
                <p className="text-sm text-slate-400">
                  {scanResult.hotspots.length} hotspots
                </p>
              ) : null}
            </div>

            {scanResult ? (
              <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {scanResult.hotspots.map((hotspot) => {
                  const isSelected = selectedHotspotId === hotspot.id
                  const isApproved = approvedHotspotIds.includes(hotspot.id)

                  return (
                    <button
                      key={hotspot.id}
                      type="button"
                      onClick={() => setSelectedHotspotId(hotspot.id)}
                      className={`rounded-2xl border p-5 text-left transition hover:border-sky-500/60 hover:bg-slate-800 ${
                        isSelected ? 'border-sky-500 bg-slate-800' : 'border-slate-800 bg-slate-950'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <span
                          className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${severityStyles[hotspot.severity]}`}
                        >
                          {hotspot.severity}
                        </span>
                        {isApproved ? (
                          <span className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-200">
                            Approved
                          </span>
                        ) : null}
                      </div>

                      <h3 className="mt-4 text-base font-semibold text-white">
                        {hotspot.title}
                      </h3>
                      <p className="mt-3 text-sm leading-6 text-slate-300">
                        {hotspot.summary}
                      </p>

                      {hotspot.narrative ? (
                        <div className="mt-4 border-t border-slate-800 pt-4">
                          <p className="text-sm leading-6 text-slate-400 italic">
                            {hotspot.narrative}
                          </p>
                        </div>
                      ) : null}

                      <div className="mt-4 flex items-center justify-between text-sm text-slate-400">
                        <span className="capitalize">{hotspot.category}</span>
                        <span>{hotspot.affected_files.length} files</span>
                      </div>
                    </button>
                  )
                })}
              </div>
            ) : (
              <EmptyState message="Run a scan to populate readiness, hotspots, and roadmap recommendations." />
            )}
          </section>

          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div>
              <h2 className="text-lg font-semibold text-white">Phased Roadmap</h2>
              <p className="mt-1 text-sm text-slate-400">
                Workstreams grouped by when they should land.
              </p>
            </div>

            {scanResult ? (
              <div className="mt-6 grid gap-4 lg:grid-cols-3">
                {PHASES.map((phase) => (
                  <RoadmapColumn
                    key={phase}
                    phase={phase}
                    workstreams={scanResult.workstreams}
                    hotspots={scanResult.hotspots}
                  />
                ))}
              </div>
            ) : (
              <EmptyState message="The roadmap will appear here after the first scan completes." />
            )}
          </section>
        </main>
      </div>

      <div
        className={`fixed inset-0 z-40 bg-slate-950/70 transition-opacity ${
          selectedHotspot ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
        }`}
        onClick={() => setSelectedHotspotId(null)}
      />

      <aside
        className={`fixed right-0 top-0 z-50 h-full w-full max-w-2xl transform overflow-y-auto border-l border-slate-800 bg-slate-900 shadow-2xl shadow-black/50 transition-transform duration-200 sm:w-[42rem] ${
          selectedHotspot ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex min-h-full flex-col">
          <div className="flex items-start justify-between gap-4 border-b border-slate-800 px-6 py-5">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">
                Hotspot Details
              </p>
              <h2 className="mt-2 text-xl font-semibold text-white">
                {selectedHotspot?.title ?? 'No hotspot selected'}
              </h2>
            </div>
            <button
              type="button"
              onClick={() => setSelectedHotspotId(null)}
              className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:border-slate-500 hover:text-white"
            >
              Close
            </button>
          </div>

          {selectedHotspot ? (
            <div className="flex-1 space-y-6 px-6 py-5">
              <div className="flex flex-wrap items-center gap-3">
                <span
                  className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${severityStyles[selectedHotspot.severity]}`}
                >
                  {selectedHotspot.severity}
                </span>
                <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-medium capitalize text-slate-300">
                  {selectedHotspot.category}
                </span>
              </div>

              <div className="space-y-3">
                <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Summary
                </h3>
                <p className="text-sm leading-7 text-slate-200">
                  {selectedHotspot.summary}
                </p>
              </div>

              <div className="space-y-3">
                <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Recommended Action
                </h3>
                <p className="text-sm leading-7 text-slate-200">
                  {selectedHotspot.recommended_action}
                </p>
              </div>

              <div className="space-y-3">
                <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Affected Files
                </h3>
                <div className="space-y-2">
                  {selectedHotspot.affected_files.map((file) => (
                    <div
                      key={file}
                      className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 font-mono text-sm text-slate-200"
                    >
                      {file}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={handleApprove}
                  disabled={isApproving}
                  className="rounded-xl bg-emerald-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300"
                >
                  {approvedHotspotIds.includes(selectedHotspot.id)
                    ? 'Approved'
                    : isApproving
                      ? 'Approving...'
                      : 'Approve'}
                </button>
              </div>

              <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-950 p-5">
                <div>
                  <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
                    Handoff Pack Preview
                  </h3>
                  <p className="mt-1 text-sm text-slate-500">
                    Structured prompt the Radar will send to IBM Bob for execution.
                  </p>
                </div>

                {isHandoffLoading ? (
                  <p className="text-sm text-slate-300">Loading handoff pack...</p>
                ) : handoffPack ? (
                  <div className="space-y-5">
                    <div className="space-y-2">
                      <h4 className="text-base font-semibold text-white">
                        {handoffPack.title}
                      </h4>
                      <p className="text-sm leading-7 text-slate-200">
                        {handoffPack.prompt}
                      </p>
                    </div>

                    <div>
                      <h5 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
                        Target Files
                      </h5>
                      <div className="mt-3 space-y-2">
                        {handoffPack.target_files.map((file) => (
                          <div
                            key={file}
                            className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 font-mono text-sm text-slate-200"
                          >
                            {file}
                          </div>
                        ))}
                      </div>
                    </div>

                    <ListBlock
                      title="Acceptance Criteria"
                      items={handoffPack.acceptance_criteria}
                    />
                    <ListBlock title="Test Plan" items={handoffPack.test_plan} />
                  </div>
                ) : (
                  <p className="text-sm text-slate-300">
                    Select a hotspot to preview its handoff guidance.
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="flex flex-1 items-center justify-center px-6 py-10 text-center text-sm text-slate-400">
              Choose a hotspot from the heatmap to inspect its details.
            </div>
          )}
        </div>
      </aside>
    </div>
  )
}

function RoadmapColumn({
  phase,
  workstreams,
  hotspots,
}: {
  phase: WorkstreamPhase
  workstreams: Workstream[]
  hotspots: Hotspot[]
}) {
  const phaseWorkstreams = workstreams.filter((workstream) => workstream.phase === phase)

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-base font-semibold text-white">{phaseLabels[phase]}</h3>
        <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-medium text-slate-300">
          {phaseWorkstreams.length} workstream{phaseWorkstreams.length === 1 ? '' : 's'}
        </span>
      </div>

      {phaseWorkstreams[0]?.rationale ? (
        <p className="mt-3 text-sm leading-6 text-slate-400 italic">
          {phaseWorkstreams[0].rationale}
        </p>
      ) : null}

      <div className="mt-4 space-y-4">
        {phaseWorkstreams.map((workstream) => (
          <div
            key={`${phase}-${workstream.impact}`}
            className="rounded-xl border border-slate-800 bg-slate-900 p-4"
          >
            <div className="flex items-center justify-between gap-4 text-sm text-slate-400">
              <span>Effort {workstream.effort}</span>
              <span>{workstream.hotspot_ids.length} hotspot{workstream.hotspot_ids.length === 1 ? '' : 's'}</span>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-200">
              {workstream.impact}
            </p>
            <div className="mt-4 space-y-2">
              {workstream.hotspot_ids.map((hotspotId) => {
                const hotspot = hotspots.find((item) => item.id === hotspotId)
                if (!hotspot) {
                  return null
                }

                return (
                  <div
                    key={hotspot.id}
                    className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3"
                  >
                    <p className="text-sm font-medium text-white">{hotspot.title}</p>
                    <p className="mt-1 text-sm text-slate-400">
                      {hotspot.severity} · {hotspot.category}
                    </p>
                  </div>
                )
              })}
            </div>
          </div>
        ))}

        {phaseWorkstreams.length === 0 ? (
          <p className="text-sm text-slate-400">No workstreams assigned.</p>
        ) : null}
      </div>
    </div>
  )
}

function ListBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h5 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
        {title}
      </h5>
      <ul className="mt-3 space-y-2">
        {items.map((item) => (
          <li
            key={item}
            className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm leading-6 text-slate-200"
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="mt-6 rounded-2xl border border-dashed border-slate-700 bg-slate-950 px-4 py-10 text-center text-sm text-slate-400">
      {message}
    </div>
  )
}

async function fetchJson<T>(input: string, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init)

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }

  return (await response.json()) as T
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }

  return 'Something went wrong while talking to the API.'
}

export default App
