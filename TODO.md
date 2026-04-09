# TODO / Progress

## Completed foundation and core platform work
- [x] Refactored Python package structure
  - Broke the crawler into a maintainable package layout instead of a single-script flow.
  - Established clearer module boundaries for config, scanners, outputs, pipeline, cache, scoring, and Web UI.
- [x] GitHub Actions workflow with tests
  - Added CI coverage so repository changes run through automated checks before crawler/report steps.
  - Standardized the project around repeatable GitHub-hosted runs.
- [x] Rules files and config-driven scoring
  - Added rules-based include/ignore/alias/scoring control so behavior is not hardcoded everywhere.
  - Made future tuning easier without large code rewrites.
- [x] Review state persistence
  - Added durable review-state storage so manual decisions survive future scans.
  - Supports statuses, notes, and reviewer attribution across reruns.
- [x] Improved evidence fields and report visibility
  - Expanded evidence output so a result explains why it was found instead of appearing as an opaque hit.
  - Prepared the project for future evidence-strength scoring.

## Completed source scanners and discovery coverage
- [x] F-Droid scanner
  - Added package discovery from F-Droid-compatible indexes.
- [x] GitHub code scanner
  - Added GitHub code-search based discovery for Shizuku-related implementation evidence.
- [x] GitHub metadata scanner
  - Added repository metadata/readme discovery for Shizuku-related projects.
- [x] GitHub releases scanner
  - Added release-aware discovery that can surface repositories with actual downloadable artifacts.
- [x] GitHub forks scanner
  - Added fork discovery so maintained downstream variants can be surfaced and compared.
- [x] GitLab scanner
  - Added GitLab project discovery and lightweight enrichment.
- [x] Codeberg scanner
  - Added Codeberg project discovery and lightweight enrichment.
- [x] Plugin scanner foundation
  - Added scanner registration plumbing so future discovery sources can be added more cleanly.

## Completed output, reporting, and state artifacts
- [x] HTML report with filters
  - Added browser-readable static reporting for quick review without the Web UI server.
- [x] CSV / JSON / Markdown / stats / diff outputs
  - Standardized multiple export formats for scripting, spreadsheet review, summaries, and change tracking.
- [x] Phase 3: automated PR mode
  - Added safer automation flow for generating crawler output changes through PR-oriented CI behavior.
- [x] Phase 3: incremental scan mode
  - Added changed-only reporting flow to reduce noise and make repeated runs more reviewable.
- [x] Scanner-specific metrics expansion
  - Added per-scanner stats output to make source health and productivity visible.
- [x] More network failure simulation tests
  - Added local retry simulation coverage so transient HTTP failures are exercised in tests instead of assumed.

## Completed reliability, normalization, and quality improvements
- [x] Package-id parser fix for quoted applicationId syntax
  - Fixed normalization/parser behavior for common Android build-file syntax.
- [x] Stronger artifact verification
  - Added artifact-quality heuristics for APK/AAB/download-style release assets.
- [x] Fork lineage analysis
  - Added parent/ahead-behind context so maintained forks are easier to evaluate.
- [x] More scanner tests
  - Expanded coverage around scanner behavior and registry/preset behavior.
- [x] Better retry/backoff controls
  - Centralized retry behavior for transient scanner network failures.
- [x] GitLab/Codeberg enrichment improvements
  - Added extra metadata such as tag/release/homepage hints when source APIs provide them.
- [x] Release quality scoring refinements
  - Improved ranking based on artifact/installability quality rather than naive presence alone.
- [x] Scanner enable/disable presets
  - Added source presets like `full`, `quick`, `github-only`, `fdroid-only`, and `non-github`.
- [x] Per-scanner runtime metrics
  - Added elapsed-time and item-count visibility per source.
- [x] Retry count / rate-limit / failure metrics
  - Added request, retry, 429-hit, and failure counters into scanner stats.

## Completed Web UI and review workflow work
- [x] Web UI / review dashboard
  - Added a built-in HTTP review UI backed by crawler cache files.
  - Supports browsing, detail inspection, and writeback review state editing.
- [x] Browser-based review actions for confirmed / reviewed / false_positive / archived
  - Added one-click status actions to reduce manual review friction.
- [x] In-browser review note editing with writeback to review state
  - Added notes/reviewer editing directly in the browser UI.
- [x] Metrics dashboard / richer observability view
  - Added a Web UI stats panel backed by `scan_stats.json` for totals and per-scanner observability.
- [x] Web UI mobile layout improvements
  - Improved narrow-screen layout, spacing, tap targets, and mobile navigation behavior.
- [x] Web UI language badge / translate action
  - Added language-awareness helpers in the UI for obviously non-English/non-Latin-script text.
- [x] Web UI description rendering fix
  - Fixed raw HTML-like description blobs so they render as readable text rather than markup noise.
- [x] Web UI language badge behavior fix
  - Removed misleading broad labels like “Latin script” and limited translation affordances to more relevant cases.
- [x] AppConfig Web UI default compatibility fix
  - Restored backwards-compatible defaults so older tests and direct config construction paths still work.
- [x] Web UI escape warning fix
  - Fixed the embedded HTML string escaping issue that produced Python warnings in CI.

## Completed Option C foundation (strict vs broad discovery)
- [x] Option C foundation: discovery-mode switch (`strict` / `broad`)
  - Added a configurable mode switch so the crawler can move toward dual behavior instead of one fixed search profile.
- [x] Option C foundation: search-pages control
  - Added paging control so discovery is no longer locked to the first page only.
- [x] Option C foundation: shared GitHub discovery query packs
  - Added reusable strict and broad query sets for GitHub discovery.
- [x] Option C foundation: broad GitHub code discovery
  - Expanded code-level discovery beyond a single exact-string query.
- [x] Option C foundation: broad GitHub metadata discovery
  - Expanded repository/readme metadata discovery with a wider query set.
- [x] Option C foundation: broad GitHub release discovery
  - Expanded release-oriented GitHub discovery using broader repository matching before release inspection.
- [x] Option C foundation: paginated GitHub discovery
  - Added multi-page retrieval so discovery can reach beyond page one.
- [x] Option C foundation: matched-query evidence recording
  - Recorded which discovery query produced each result so review and future verification are more explainable.
- [x] Option C foundation: broad query expansion tests
  - Added tests proving broad mode actually expands discovery input beyond strict mode.

## Additional recommended features not built yet
- [ ] Artifact verification beyond heuristics
  - Move from filename/asset-shape heuristics toward stronger installability or authenticity checks.
- [ ] Deeper GitLab enrichment (releases, tags, assets, better metadata)
  - Expand GitLab beyond lightweight metadata/release hints into stronger project inspection.
- [ ] Deeper Codeberg enrichment (releases, tags, assets, better metadata)
  - Expand Codeberg beyond lightweight metadata/release hints into stronger project inspection.
- [ ] More advanced plugin system
  - Evolve the current scanner foundation into a richer extension model.
- [ ] More advanced artifact/installability judgment
  - Improve release judgment beyond simple artifact presence and heuristic quality labels.

## Option C remaining work
- [ ] Strict-mode verification / evidence-strength layer (`weak` / `medium` / `strong`)
  - Add a real proof-quality model instead of treating all discovery hits as equivalent.
- [ ] Strict-mode filtering that excludes weak-only matches
  - Make strict mode actually strict by dropping shallow metadata-only hits.
- [ ] Broad-mode retention with weaker confidence instead of hard exclusion
  - Let broad mode keep exploratory hits while clearly lowering their confidence.
- [ ] Apply Option C discovery/verification split to GitLab scanner
  - Bring GitLab into the same strict-vs-broad design used for GitHub.
- [ ] Apply Option C discovery/verification split to Codeberg scanner
  - Bring Codeberg into the same strict-vs-broad design used for GitHub.
- [ ] README/source/manifest verification for stronger proof of Shizuku usage
  - Verify with stronger repository/project content inspection rather than metadata alone.
- [ ] Score/rank results using evidence strength
  - Feed proof quality into ranking so stronger evidence surfaces earlier.
- [ ] Add output/UI visibility for evidence strength
  - Surface strictness/evidence quality clearly in reports and the Web UI.
- [ ] Add full strict-vs-broad behavior tests
  - Cover filtering, ranking, pagination, and verification-mode differences in tests.

## Notes
- Current repo state includes Phase 1, Phase 2, and Phase 3 core tasks completed.
- The generated apps.html report still exists for static review, and the Web UI provides interactive review-state editing backed by cache/review_state.json.
- Option C has started. The repo now supports `--discovery-mode strict|broad` and `--search-pages`, with broader paginated GitHub discovery already in place. The main missing piece is the verification layer that differentiates strict-mode validated matches from broad-mode exploratory matches.
