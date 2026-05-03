# Bob Session 3 — Hero Patch Recording

Raw screen recording of IBM Bob applying the **CVE-2015-7501** fix on the petclinic `legacy-baseline` branch.

**Watch:** https://youtu.be/-6QBU4KeKMw

## What the recording shows

1. The Bob session #3 prompt being submitted in Plan mode (no narration — silent capture)
2. Bob's reasoning trace identifying `commons-collections:commons-collections:3.2.1` in `pom.xml`
3. The proposed dependency swap to `org.apache.commons:commons-collections4:4.4`
4. Manual approval of the patch (the human-in-the-loop step)
5. Bob applying the edit and running `./mvnw validate` and `./mvnw test-compile` (both BUILD SUCCESS)
6. `git diff pom.xml` showing the exact change

## Outcome

- **CVE-2015-7501 (CVSS 9.8)** — Remote code execution via `InvokerTransformer` deserialization gadget chain
- **Files modified:** `pom.xml` only (1 file, +3 / -3 lines)
- **Code impact:** zero — no Java files imported the old package, the dependency was declared but unused
- **Verification:** 47 source files compiled, 13 test files compiled, no regressions

## Cost

**0.99 Bobcoins** — well under the ~5-coin estimate for this session.

## Before / after demonstration

After the patch landed on `legacy-baseline`, the live Radar dashboard re-scanned the same branch and produced:

| | Before patch | After patch |
|---|---|---|
| Readiness score | 55 / 100 | **80 / 100** |
| Hotspots | 3 (Critical + High + Medium) | 2 (High + Medium) |
| Critical CVE | Present | **Eliminated** |
| Now-phase workstreams | 1 (the CVE) | **0** |

The before/after dashboard screenshots are in this same folder (`consumption_summary.png`, `after_patch_dashboard.png`).

## Note on file size

The raw `.mov` recording is 149 MB, which exceeds GitHub's 100 MB per-file limit. The video is hosted on YouTube (unlisted) at the link above and is not committed to this repository. The `.gitignore` excludes `bob_sessions/**/*.mov` and `bob_sessions/**/*.mp4` to prevent accidental commits.
