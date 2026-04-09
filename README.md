# App Crawler (Refactored Python Edition)

A Python crawler for discovering Android apps and repositories that use **Shizuku** or related integrations. It scans F-Droid-style indexes and GitHub, merges and scores results, and generates reports that can be used locally or through **GitHub Actions**.

This version is structured as a maintainable Python package rather than a single-purpose script.

---

## What it does

The crawler can:

- scan F-Droid-compatible indexes
- scan GitHub repositories and code for likely Shizuku use
- merge duplicate results deterministically
- score results by confidence and usefulness
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
  - `scoring.py` — confidence/usefulness scoring
  - `outputs.py` — markdown/json/csv/html outputs
  - `cache.py` — local cache handling
  - `known.py` — existing-known-app filtering helpers
  - `utils.py` — shared utility functions
  - `scanners/` — source scanners
- `.github/workflows/run-crawler.yml` — GitHub Actions workflow
- `requirements.txt` — Python dependencies
- `pyproject.toml` — project metadata
- `ignore_list.lst` — ignore list

---

## Requirements

- Python 3.11+ recommended
- a GitHub token for broader API access is helpful

---

## Install locally

### 1. Clone the repo

```bash
git clone https://github.com/YOURNAME/YOURREPO.git
cd YOURREPO
```

### 2. Install dependencies

```bash
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

---

## Important CLI options

Run this to see all available flags:

```bash
python main.py --help
```

Common options include:

- `--json` — write JSON output
- `--csv` — write CSV output
- `--html` — write HTML output
- `--summary-file SUMMARY.md` — choose markdown output filename
- `--stats-file scan_stats.json` — choose stats filename
- `--diff-file scan_diff.json` — choose diff filename
- `--recent-days 90` — define what counts as recent
- `--process-count N` — control parallel GitHub scanner workers
- `--dry-run` — preview without committing state changes
- `--no-cache` — ignore cache for the current run
- `--log-level INFO` — choose log verbosity

---

## Output files

### `SUMMARY.md`
Human-readable markdown summary.

### `apps.json`
Structured machine-readable result set.

### `apps.csv`
Spreadsheet-friendly export.

### `apps.html`
Simple HTML report for quick browsing.

### `scan_stats.json`
Summary statistics for the run.

### `scan_diff.json`
What changed since the last run.

### `cache/`
Stores run cache/history used for comparison across runs.

---

## Ignore list

Use `ignore_list.lst` to exclude known unwanted matches.

You can ignore by:
- app name
- exact URL

---

## How scoring works

The refactored app uses two main ideas:

### Confidence
How likely it is that the app/repo genuinely uses Shizuku.

### Usefulness
How useful the result is in practice.

Example:
- a repo mentioning Shizuku only in docs may be low usefulness
- an actively maintained project with releases may be high usefulness

---

## GitHub Actions usage

This repo includes a workflow at:

```text
.github/workflows/run-crawler.yml
```

### What it does

It can:
- run manually from the Actions tab
- run on a schedule
- optionally scan a separate target repository/list repo
- upload generated reports as artifacts
- optionally commit report updates back to the target repo

### Recommended secret

Add this repository secret if you want stronger GitHub API access:

- `GH_PAT`

If absent, the workflow falls back to the built-in `github.token`.

### Manual run

1. Open **Actions**
2. Select **Run crawler**
3. Run the workflow

---

## Typical GitHub Actions setup

If you want this repo to scan itself, the default workflow works as-is.

If you want this repo to scan another repo or list target, set workflow env values in the workflow file:

- `LIST_REPOSITORY`
- `LIST_REF`
- `TARGET_PATH`
- `EXTRA_ARGS`

---

## Common problems

### No GitHub results
Usually means `GITHUB_AUTH` / `GH_PAT` is missing or rate-limited.

### Empty reports
Could mean:
- no matches found
- everything matched the ignore list
- wrong target path

### HTML/JSON/CSV files not written
Make sure you passed the matching flags:

```bash
--json --csv --html
```

---

## Suggested first run

```bash
python main.py . --json --csv --html --log-level INFO
```

---

## Next improvements

This refactor is a foundation. Good next steps include:

- review workflow persistence
- rules files
- stronger evidence snippets
- GitHub releases scanner
- forks scanner
- tests expansion
- richer HTML dashboard

---

## Summary

This version is meant to be:

- easier to maintain
- easier to extend
- easier to use in CI
- easier to understand for someone new to the project
