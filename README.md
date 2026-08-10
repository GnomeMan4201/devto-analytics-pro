<!-- GnomeMan4201 // badBANANA research -->

<div align="center">

<img src="assets/banner.svg" alt="DEV.to Analytics Pro banner" width="100%"/>

# DEV.to Analytics Pro

**Local CLI analytics for DEV.to authors: content performance, audience signals, publishing patterns, tag intelligence, and exportable reports.**

[![CI](https://github.com/GnomeMan4201/devto-analytics-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/GnomeMan4201/devto-analytics-pro/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](#requirements)
[![Local first](https://img.shields.io/badge/data-local--first-222222)](#privacy-and-data-handling)

</div>

---

## What it does

DEV.to Analytics Pro turns the authenticated DEV.to API into a terminal-native research and publishing dashboard. It is built for authors who want more than aggregate view counts: it correlates article performance with tags, publish timing, follower activity, repeat commenters, reading-list behavior, content characteristics, and cross-platform signals.

The tool can analyze:

- article views, reactions, comments, engagement rate, and growth over time
- top and underperforming articles over selectable date windows
- tag performance and missing-tag opportunities
- multi-part series performance and reader drop-off
- day/hour publishing performance
- follower growth around publication events
- repeat commenters and follower/commenter overlap
- commenter profile enrichment through DEV.to profile data
- article-body characteristics, vocabulary, tooling mentions, and link density
- reading-list and followed-tag behavior
- competitive activity in selected DEV.to tags
- JSON and CSV exports for downstream analysis

No hosted dashboard or database is required. Analysis runs from the local Python process and output stays on the machine unless you explicitly export or share it.

---

## Quick start

### 1. Clone and create an isolated environment

```bash
git clone https://github.com/GnomeMan4201/devto-analytics-pro.git
cd devto-analytics-pro
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Verify the installation

The fastest dependency/CLI smoke check does not contact DEV.to:

```bash
python dev.py --help
```

For the repository test suite:

```bash
pip install pytest
python -m pytest -q
```

The current suite primarily validates importability and basic project structure. API-backed analytics depend on live DEV.to responses and a valid API key and should be treated separately from the offline smoke tests.

### 3. Add your DEV.to API key

Create an API key in your DEV.to account settings, then pass it at runtime:

```bash
python dev.py --api-key "$DEVTO_API_KEY" --overview
```

A shell environment variable keeps the key out of command history more reliably than pasting the literal key into repeated commands:

```bash
export DEVTO_API_KEY='your-key-here'
python dev.py --api-key "$DEVTO_API_KEY" --full-report
```

Do not commit API keys, exported private account data, or shell history containing credentials.

---

## Common workflows

### Portfolio overview

```bash
python dev.py --api-key "$DEVTO_API_KEY" --overview
```

### Top articles by engagement

```bash
python dev.py --api-key "$DEVTO_API_KEY" --top 20 --sort engagement
```

### Last 90 days of tag performance

```bash
python dev.py --api-key "$DEVTO_API_KEY" --tags --days 90
```

### Audience and commenter analysis

```bash
python dev.py --api-key "$DEVTO_API_KEY" --follower-correlation
python dev.py --api-key "$DEVTO_API_KEY" --commenters
python dev.py --api-key "$DEVTO_API_KEY" --loyal-readers
python dev.py --api-key "$DEVTO_API_KEY" --commenter-enrichment --enrich-top 15
```

### Publishing and content intelligence

```bash
python dev.py --api-key "$DEVTO_API_KEY" --publish-heatmap
python dev.py --api-key "$DEVTO_API_KEY" --series
python dev.py --api-key "$DEVTO_API_KEY" --content-analysis
python dev.py --api-key "$DEVTO_API_KEY" --tag-fix
python dev.py --api-key "$DEVTO_API_KEY" --insights
```

### Full report

```bash
python dev.py --api-key "$DEVTO_API_KEY" --full-report
```

`--full-report` intentionally performs many API-backed analyses and can take longer than a single focused command.

---

## Export

Export article data and summary metrics for local notebooks, spreadsheets, or archival workflows:

```bash
python dev.py --api-key "$DEVTO_API_KEY" --export-json analytics.json
python dev.py --api-key "$DEVTO_API_KEY" --export-csv analytics.csv
```

You can combine exports with a date filter:

```bash
python dev.py --api-key "$DEVTO_API_KEY" --days 90 --export-csv last-90-days.csv
```

---

## CLI reference

Run the authoritative command reference at any time:

```bash
python dev.py --help
```

Major analysis flags include:

| Flag | Purpose |
|---|---|
| `--overview` | Aggregate article statistics |
| `--top N` | Rank the top N articles |
| `--sort` | Sort by views, reactions, comments, or engagement |
| `--tags` | Tag performance analysis |
| `--growth` | Month-over-month growth |
| `--underperformers` | Detect significant underperformance |
| `--series` | Analyze multi-part article series |
| `--publish-heatmap` | Compare publish day/hour performance |
| `--follower-correlation` | Relate follower growth to publication events |
| `--commenters` | Rank repeat commenters |
| `--loyal-readers` | Cross-reference followers and commenters |
| `--commenter-enrichment` | Enrich top commenters with DEV.to profile data |
| `--content-analysis` | Analyze article-body characteristics |
| `--reading-list` | Compare consumed topics with published topics |
| `--followed-tags` | Compare followed tags with writing behavior |
| `--competitive-tags` | Inspect current activity in primary tags |
| `--tag-fix` | Suggest relevant tags missing from article metadata |
| `--insights` | Produce synthesized findings and recommended actions |
| `--full-report` | Run the broad analysis pipeline |
| `--export-json FILE` | Export JSON |
| `--export-csv FILE` | Export CSV |

---

## Requirements

- Python 3
- a DEV.to account
- a DEV.to API key for authenticated analytics
- network access when running API-backed commands

Runtime Python dependencies are defined in `requirements.txt`:

- `requests`
- `matplotlib`
- `seaborn`
- `numpy`

`pytest` is only needed to run the repository test suite.

---

## Privacy and data handling

The tool requests account and content data from DEV.to only when a command needs it. Some analyses may retrieve follower, commenter, reading-list, profile, or article-body information. Treat exported JSON/CSV as potentially sensitive research data even when much of the underlying DEV.to activity is public.

Recommended practice:

- keep the API key in an environment variable
- keep exports out of version control
- review generated datasets before sharing
- use the smallest analysis command that answers the question when you do not need the full report

---

## Testing model

There are two different validation layers:

1. **Offline smoke validation** — importing the module, checking syntax/project structure, and exercising the CLI help path.
2. **Live integration behavior** — commands that depend on DEV.to API availability, authentication, pagination, and the shape of returned account data.

That distinction is intentional. A green local smoke test confirms that the repository is runnable; it does not prove that every external DEV.to endpoint is currently available or unchanged.

---

## Project layout

```text
devto-analytics-pro/
├── dev.py                  # CLI and analytics engine
├── requirements.txt        # runtime dependencies
├── tests/                  # pytest smoke/basic tests
├── .github/workflows/      # CI automation
└── assets/                 # repository artwork
```

---

## Intended use

This project is for first-party analytics, publishing research, and audience analysis around accounts and content you are authorized to access. It is particularly useful for researchers and technical writers who want reproducible, local analysis instead of relying exclusively on platform dashboards.

---

## Author

**GnomeMan4201** — independent security researcher / badBANANA research.

<div align="center">

<img src="assets/bad_banana_end.png" width="460" alt="badBANANA end mark" />

</div>
