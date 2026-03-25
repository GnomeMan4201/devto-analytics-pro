# devto-analytics-pro

**Article performance analytics for DEV.to writers — tag analysis, growth trends, and engagement tracking.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](#)
[![DEV.to](https://img.shields.io/badge/dev.to-gnomeman4201-black?logo=dev.to)](https://dev.to/gnomeman4201)

---

DEV.to's built-in dashboard shows you totals. This shows you trends. Pull your article data via the DEV.to API and get tag performance breakdowns, month-over-month growth, engagement rates, reading time analysis, and underperformer detection — all exportable to JSON or CSV.

---

## Features

- Total views, reactions, comments, and engagement rates
- Top performers by views, reactions, or engagement
- Tag performance analysis — which tags drive traffic
- Reading time vs engagement correlation
- Month-over-month growth tracking
- Underperformer detection
- Export to JSON or CSV

---

## Usage
```bash
git clone https://github.com/GnomeMan4201/devto-analytics-pro.git
cd devto-analytics-pro
pip install -r requirements.txt
export DEVTO_API_KEY=your_key_here
python3 dev.py
```

---

## Tests
```bash
python3 -m pytest tests/
```

---

*devto-analytics-pro // badBANANA research // GnomeMan4201*

---

## Demo

<p align="center">
  <img src="assets/devto_analytics_demo.png" alt="devto-analytics-pro full report output" width="780"/>
</p>
