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

---

## Repository layout

- `main.py` — small entry script
- `app_crawler/` — main Python package
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

### Run tests

```bash
pytest -q
```

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
