

# DEV.to Analytics Pro

> Advanced analytics and insights for your DEV.to articles - because the built-in dashboard isn't enough.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

##  Why This Tool?

DEV.to's built-in analytics are good, but they're missing critical insights:
- ❌ No trend analysis over time
- ❌ Can't compare tag performance
- ❌ Limited export options
- ❌ No way to identify underperforming content

**DEV.to Analytics Pro solves this.**

##  Features

-  **Comprehensive Overview** - Total views, reactions, comments, and engagement rates
-  **Top Performers** - Identify your best articles by views, reactions, or engagement
-  **Tag Analysis** - See which tags drive the most traffic
-  **Reading Time Insights** - Understand how article length affects performance
-  **Growth Trends** - Track your progress month over month
-  **Underperformer Detection** - Find articles that need improvement
-  **Export Data** - Save to JSON or CSV for further analysis

##  Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/GnomeMan4201/devto-analytics-pro.git
cd devto-analytics-pro

# Install dependencies
pip install -r requirements.txt
Get Your API Key
Go to DEV.to Settings
Scroll to "DEV Community API Keys"
Generate a new key (read-only permissions are sufficient)
Basic Usage
# Full analytics report
python3 dev.py --api-key YOUR_API_KEY --full-report

# Quick overview
python3 dev.py --api-key YOUR_API_KEY --overview

# Top 20 articles by engagement
python3 dev.py --api-key YOUR_API_KEY --top 20 --sort engagement
📖 Usage Examples
Analyze Last 30 Days
python3 dev.py --api-key YOUR_KEY --overview --days 30
Find Underperforming Articles
python3 dev.py --api-key YOUR_KEY --underperformers --days 60
Tag Performance Analysis
python3 dev.py --api-key YOUR_KEY --tags --days 90
Export to CSV
python3 dev.py --api-key YOUR_KEY --export-csv my_analytics.csv
📊 Sample Output
============================================================
📊 DEV.TO ANALYTICS OVERVIEW (all time)
============================================================
📝 Total Articles:      16
👀 Total Views:         983
❤️  Total Reactions:     25
💬 Total Comments:      0
📈 Avg Views/Article:   61
🎯 Engagement Rate:     4.50%
============================================================
 
Contributions are welcome. 

Built by @GnomeMan4201 - Security researcher who got tired of not having proper analytics.
 
