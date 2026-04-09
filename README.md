# App Crawler (Refactored Python Edition)

A Python crawler for discovering Android apps and repositories that use **Shizuku** or related integrations. It scans F-Droid-style indexes and GitHub, merges and scores results, persists review state, and generates reports that can be used locally or through **GitHub Actions**.

This version is structured as a maintainable Python package rather than a single-purpose script.

---

## What it does

The crawler can:

- scan F-Droid-compatible indexes
- scan GitHub repositories and code for likely Shizuku use
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

---

## Repository layout

- `main.py` — small entry script
- `app_crawler/` — main Python package
  - `cli.py` — CLI entry
  - `config.py` — configuration and CLI args
  - `models.py` — data models
  - `pipeline.py` — scan pipeline
  - `normalize.py` — normalization helpers
  - `rules.py` — rule loading and scoring config
  - `scoring.py` — confidence/usefulness scoring
  - `outputs.py` — markdown/json/csv/html outputs
  - `cache.py` — local cache + review state handling
  - `known.py` — existing-known-app filtering helpers
  - `utils.py` — shared utility functions
  - `scanners/` — source scanners
- `rules/` — config-driven ignore/include/alias/scoring files
- `tests/` — unit tests
- `.github/workflows/run-crawler.yml` — GitHub Actions workflow
- `requirements.txt` — Python dependencies
- `pyproject.toml` — project metadata
- `ignore_list.lst` — flat ignore list

---

## Install locally

```bash
git clone https://github.com/YOURNAME/YOURREPO.git
cd YOURREPO
python -m pip install --upgrade pip
pip install -r requirements.txt
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

### With a GitHub token

```bash
export GITHUB_AUTH="your_token_here"
python main.py . --json --csv --html
```

### Dry run

```bash
python main.py . --dry-run
```

### Run tests

```bash
pytest -q
```

---

## Rules files

The crawler now supports rule files in `rules/`:

- `ignore.yaml` — permanent ignores
- `include.yaml` — forced include names/urls
- `aliases.yaml` — known name aliases
- `rules.yaml` — confidence/usefulness scoring markers

You can edit these files without changing Python code.

---

## Review state

Review decisions are persisted in:

```text
cache/review_state.json
```

This file stores fields like:
- `status`
- `review_notes`
- `reviewed_at`
- `reviewed_by`

The crawler reapplies this state on future runs using the app identity key.

---

## Important CLI options

```bash
python main.py --help
```

Common options include:
- `--json`
- `--csv`
- `--html`
- `--summary-file SUMMARY.md`
- `--stats-file scan_stats.json`
- `--diff-file scan_diff.json`
- `--recent-days 90`
- `--process-count N`
- `--dry-run`
- `--no-cache`
- `--log-level INFO`

---

## Output files

- `SUMMARY.md` — human-readable summary
- `apps.json` — structured output
- `apps.csv` — spreadsheet-friendly export
- `apps.html` — quick review dashboard
- `scan_stats.json` — run statistics
- `scan_diff.json` — what changed since last run
- `cache/current_run.json` — persisted run cache
- `cache/review_state.json` — persisted review state

---

## GitHub Actions usage

This repo includes a workflow at:

```text
.github/workflows/run-crawler.yml
```

It will:
- install dependencies
- run tests
- run the crawler
- upload generated reports as artifacts
- optionally commit report updates back to a target repo

### Recommended secret

Add this repository secret if you want stronger GitHub API access:
- `GH_PAT`

If absent, the workflow falls back to the built-in `github.token`.

### Manual run

1. Open **Actions**
2. Select **Run crawler**
3. Run the workflow

---

## Suggested first run

```bash
python main.py . --json --csv --html --log-level INFO
```

Then check:
- `apps.html`
- `scan_diff.json`
- `cache/review_state.json`

---

## Phase 1 included here

This repo now includes:
- rules files
- config-driven scoring
- persisted review state
- improved evidence visibility in outputs
- unit tests
- workflow test step

Next likely improvements:
- GitHub releases scanner
- fork scanner
- stronger HTML dashboard
- richer APK enrichment
