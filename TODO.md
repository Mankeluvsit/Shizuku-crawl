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

## In progress
- [ ] Release quality scoring refinements

## Next up
- [ ] Scanner-specific metrics expansion
- [ ] Scanner enable/disable presets
- [ ] More network failure simulation tests
- [ ] Web UI / review dashboard

## Additional recommended features not built yet
- [ ] Real Web UI / review dashboard
- [ ] Browser-based review actions for confirmed / reviewed / false_positive / archived
- [ ] In-browser review note editing with writeback to review state
- [ ] Artifact verification beyond heuristics
- [ ] Deeper GitLab enrichment (releases, tags, assets, better metadata)
- [ ] Deeper Codeberg enrichment (releases, tags, assets, better metadata)
- [ ] Per-scanner runtime metrics
- [ ] Retry count / rate-limit / failure metrics
- [ ] Scanner presets like --github-only / --fdroid-only / --full / --quick
- [ ] More advanced plugin system
- [ ] Metrics dashboard / richer observability view
- [ ] More advanced artifact/installability judgment

## Notes
- Current repo state includes Phase 1, Phase 2, and partial Phase 3.
- Phase 3 now includes safer CI automation, incremental reporting, broader source coverage, scanner registration plumbing, artifact-quality heuristics, fork lineage reporting, broader scanner test coverage, shared retry/backoff behavior for network scanners, and better GitLab/Codeberg metadata enrichment.
- The generated apps.html report exists, but it is a static report and not the planned real Web UI.
