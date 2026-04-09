# App Crawler (Refactored Python Edition)

A Python crawler for discovering Android apps and repositories that use **Shizuku** or related integrations. It scans F-Droid-style indexes, GitHub, GitLab, and Codeberg, merges and scores results, persists review state, and generates reports that can be used locally or through **GitHub Actions**.

This version is structured as a maintainable Python package rather than a single-purpose script.

---

## What it does

The crawler can:

- scan F-Droid-compatible indexes
- scan GitHub repositories and code for likely Shizuku use
- scan GitLab public projects for Shizuku-related metadata
- scan Codeberg public repositories for Shizuku-related metadata
- register scanners through a central scanner registry foundation
- merge duplicate results deterministically
- score results by confidence and usefulness using rules
- persist review state across runs
- keep cache/history across runs
- generate multiple outputs:
  - `SUMMARY.md`
  - `apps.json`
  - `apps.csv`
  - `apps.html`
  - `scan_stats.json`
  - `scan_diff.json`
- optionally generate **incremental reports** that contain only new or changed entries compared with the prior cached run
- apply artifact-quality heuristics to release assets such as APK/AAB presence, split-vs-universal hints, and checksum/signature hints
- annotate GitHub forks with lineage details such as parent repository, branch divergence counts, and whether the fork appears meaningfully ahead of the parent
- use shared retry/backoff handling for network scanners to reduce transient HTTP failures
- enrich GitLab and Codeberg findings with better homepage/tag/release hints when available
- refine scoring based on artifact quality, fork lead signals, and richer release hints instead of only simple download presence
- emit scanner-specific metrics such as runtime, item counts, and error state in stats output
- support scanner presets such as `full`, `quick`, `github-only`, `fdroid-only`, and `non-github`
- serve a built-in Web UI for reviewing and editing review state

---

## Repository layout

- `main.py` — small entry script
- `app_crawler/` — main Python package
- `app_crawler/http.py` — shared HTTP retry/backoff helpers
- `app_crawler/release_assets.py` — release asset classification heuristics
- `app_crawler/scanners/registry.py` — scanner registration foundation
- `app_crawler/webui.py` — built-in review dashboard server
- `rules/` — config-driven ignore/include/alias/scoring files
- `tests/` — unit tests
- `.github/workflows/run-crawler.yml` — test + scan workflow
- `.github/workflows/run-crawler-pr.yml` — test + scan + open PR workflow
- `TODO.md` — progress tracking
- `ignore_list.lst` — flat ignore list

---

## Install locally

```bash
git clone https://github.com/YOURNAME/YOURREPO.git
cd YOURREPO
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

---

## Run locally

### Basic run

```bash
python main.py .
```

### With JSON, CSV, and HTML outputs

```bash
python main.py . --json --csv --html
```

### Incremental report mode

```bash
python main.py . --json --csv --html --incremental
```

This mode keeps the full cache, but only writes report outputs for entries that are new or changed compared with the previous cached run.

### With a GitHub token

```bash
export GITHUB_AUTH="your_token_here"
python main.py . --json --csv --html
```

### Scanner presets

```bash
python main.py . --preset full
python main.py . --preset quick
python main.py . --preset github-only
python main.py . --preset fdroid-only
python main.py . --preset non-github
```

These presets make it easier to control source breadth without manually editing code.

### Start the Web UI

```bash
python main.py . --webui
python main.py . --webui --webui-host 0.0.0.0 --webui-port 8765
```

The Web UI reads from `cache/current_run.json` and writes review updates to `cache/review_state.json`.

### Run tests

```bash
pytest -q
```

---

## Web UI

The built-in review dashboard provides:

- search/filter over discovered apps
- detail view with evidence, scanner, quality, and lineage hints
- one-click status actions for `confirmed`, `reviewed`, `false_positive`, and `archived`
- note editing in-browser
- writeback to `cache/review_state.json`

The UI is intentionally small and framework-free so it runs anywhere Python runs.

---

## Scanner metrics

`scan_stats.json` now includes scanner-specific metrics such as:

- scanner runtime in milliseconds
- item counts returned per scanner
- scanner error state and last error message when a scanner fails
- request counts
- retry counts derived from response retry history
- rate-limit hit counts
- failed request counts

This makes it easier to spot slow or flaky sources in CI and scheduled runs.

---

## Quality-aware scoring

Usefulness scoring is now influenced by more than just “has downloads”. It also reacts to:

- stronger artifact quality labels such as `strong` or `installable`
- checksum/signature-style assets
- universal APK hints
- forks that appear meaningfully ahead of their parent
- recent update signals when installable assets are not present

This helps surface more promising candidates higher in the generated reports.

---

## Retry/backoff behavior

Network scanners now use a shared HTTP session with retries and backoff for transient failures such as:

- `429 Too Many Requests`
- `500`, `502`, `503`, `504`

This improves reliability for scheduled runs and CI without changing the crawler interface.

The test suite now includes local HTTP-server simulations that return transient `503` and `429` responses before succeeding, so retry behavior is exercised rather than only configured.

---

## GitLab/Codeberg enrichment hints

GitLab and Codeberg findings now try to pull extra metadata when available:

- homepage / external website links
- release or latest-tag hints
- detected tag names and updated release timestamps
- improved description composition when source metadata is sparse

These are lightweight enrichment hints and may vary by public API response quality.

---

## Artifact verification hints

Release assets are now annotated with simple quality heuristics:

- whether an `.apk` or `.aab` exists
- whether a filename looks like a split APK or a universal APK
- whether checksum/signature style files are present in release assets
- a compact quality label shown in outputs

These are heuristics for review, not cryptographic validation.

---

## Fork lineage hints

GitHub fork results now include fork lineage metadata when available:

- parent repository full name
- ahead/behind counts relative to parent default branch
- whether the fork looks meaningfully ahead of the parent

These details are shown in outputs to make maintained forks easier to review.

---

## GitHub Actions usage

### Standard workflow

```text
.github/workflows/run-crawler.yml
```

Runs tests, runs the crawler, and uploads artifacts.

### PR workflow

```text
.github/workflows/run-crawler-pr.yml
```

Runs tests, runs the crawler in incremental mode, and opens a pull request with changed reports instead of writing directly to `main`.

### Recommended secret

Add this repository secret if you want stronger GitHub API access:
- `GH_PAT`

If absent, workflows fall back to the built-in `github.token`.

---

## Progress tracking

See:

```text
TODO.md
```

This file tracks what is done and what is next.
