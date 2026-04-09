# TODO / Progress

## Completed
- [x] Refactored Python package structure
- [x] GitHub Actions workflow with tests
- [x] Rules files and config-driven scoring
- [x] Review state persistence
- [x] Improved evidence fields and report visibility
- [x] F-Droid scanner
- [x] GitHub code scanner
- [x] GitHub metadata scanner
- [x] GitHub releases scanner
- [x] GitHub forks scanner
- [x] HTML report with filters
- [x] CSV / JSON / Markdown / stats / diff outputs
- [x] Package-id parser fix for quoted applicationId syntax
- [x] Phase 3: automated PR mode
- [x] Phase 3: incremental scan mode
- [x] GitLab scanner
- [x] Codeberg scanner
- [x] Plugin scanner foundation
- [x] Stronger artifact verification
- [x] Fork lineage analysis
- [x] More scanner tests
- [x] Better retry/backoff controls
- [x] GitLab/Codeberg enrichment improvements
- [x] Release quality scoring refinements
- [x] Scanner-specific metrics expansion
- [x] Scanner enable/disable presets
- [x] More network failure simulation tests
- [x] Web UI / review dashboard
- [x] Web UI mobile layout improvements
- [x] Web UI language badge / translate action
- [x] Web UI description rendering fix
- [x] Web UI language badge behavior fix
- [x] AppConfig Web UI default compatibility fix
- [x] Web UI escape warning fix
- [x] Option C foundation: discovery-mode switch (`strict` / `broad`)
- [x] Option C foundation: search-pages control
- [x] Option C foundation: shared GitHub discovery query packs
- [x] Option C foundation: broad GitHub code discovery
- [x] Option C foundation: broad GitHub metadata discovery
- [x] Option C foundation: broad GitHub release discovery
- [x] Option C foundation: paginated GitHub discovery
- [x] Option C foundation: matched-query evidence recording
- [x] Option C foundation: broad query expansion tests

## Additional recommended features not built yet
- [x] Browser-based review actions for confirmed / reviewed / false_positive / archived
- [x] In-browser review note editing with writeback to review state
- [ ] Artifact verification beyond heuristics
- [ ] Deeper GitLab enrichment (releases, tags, assets, better metadata)
- [ ] Deeper Codeberg enrichment (releases, tags, assets, better metadata)
- [x] Per-scanner runtime metrics
- [x] Retry count / rate-limit / failure metrics
- [x] Scanner presets like --github-only / --fdroid-only / --full / --quick
- [ ] More advanced plugin system
- [x] Metrics dashboard / richer observability view
- [ ] More advanced artifact/installability judgment

## Option C remaining work
- [ ] Strict-mode verification / evidence-strength layer (`weak` / `medium` / `strong`)
- [ ] Strict-mode filtering that excludes weak-only matches
- [ ] Broad-mode retention with weaker confidence instead of hard exclusion
- [ ] Apply Option C discovery/verification split to GitLab scanner
- [ ] Apply Option C discovery/verification split to Codeberg scanner
- [ ] README/source/manifest verification for stronger proof of Shizuku usage
- [ ] Score/rank results using evidence strength
- [ ] Add output/UI visibility for evidence strength
- [ ] Add full strict-vs-broad behavior tests

## Notes
- Current repo state includes Phase 1, Phase 2, and Phase 3 core tasks completed.
- The generated apps.html report still exists for static review, and the Web UI provides interactive review-state editing backed by cache/review_state.json.
- Option C has started. The repo now supports `--discovery-mode strict|broad` and `--search-pages`, with broader paginated GitHub discovery already in place. The main missing piece is the verification layer that differentiates strict-mode validated matches from broad-mode exploratory matches.
