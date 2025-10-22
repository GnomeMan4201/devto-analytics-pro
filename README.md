# 📊 DEV.to Analytics Pro

> Advanced analytics and insights for your DEV.to articles - because the built-in dashboard isn't enough.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Why This Tool?

DEV.to's built-in analytics are good, but they're missing critical insights:
- ❌ No trend analysis over time
- ❌ Can't compare tag performance
- ❌ Limited export options
- ❌ No way to identify underperforming content

**DEV.to Analytics Pro solves this.**

## ✨ Features

- 📈 **Comprehensive Overview** - Total views, reactions, comments, and engagement rates
- 🏆 **Top Performers** - Identify your best articles by views, reactions, or engagement
- 🏷️ **Tag Analysis** - See which tags drive the most traffic
- 📚 **Reading Time Insights** - Understand how article length affects performance
- 📊 **Growth Trends** - Track your progress month over month
- ⚠️ **Underperformer Detection** - Find articles that need improvement
- 📁 **Export Data** - Save to JSON or CSV for further analysis

## 🚀 Quick Start

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
💡 Real Insights I Discovered
Using this tool on my own 16 articles (983 total views), I found:
🎯 AI security posts get 2x average views (116 vs 61) - completely shifted my content strategy
📅 October engagement 4x better than July (12 reactions vs 9, despite fewer articles)
💬 Zero comments across all articles - identified I wasn't asking questions or prompting discussion
🏷️ Tag performance varies wildly: #ai (116 avg) vs #cybersecurity (62 avg) despite being more niche
📊 Quality > Quantity confirmed: 3 focused October articles outperformed 9 rushed July posts
📈 Engagement rate improved from 2.54% to 4.50% in 3 months by following data insights
🔧 Command-Line Arguments
Argument
Description
--api-key
Your DEV.to API key (required)
--overview
Show overview statistics
--top N
Show top N articles
--sort {views,reactions,comments,engagement}
Sort criteria
--tags
Analyze tag performance
--reading-time
Analyze by reading time
--growth
Show monthly growth trends
--underperformers
Find low-performing articles
--days N
Filter by last N days
--export-json FILE
Export to JSON
--export-csv FILE
Export to CSV
--full-report
Run complete analysis
🛠️ Requirements
requests>=2.31.0
matplotlib>=3.7.0  # Optional, for visualizations
seaborn>=0.12.0    # Optional, for visualizations
numpy>=1.24.0      # Optional, for visualizations
📝 Use Cases
📊 Content Strategy - Identify what resonates with your audience
🎯 SEO Optimization - Find high-performing tags and topics
📈 Growth Tracking - Monitor your progress over time
🔍 Content Audit - Find articles to update or improve
📑 Portfolio Analytics - Professional metrics for your writing
🤝 Contributing
Contributions are welcome! Areas for improvement:
[ ] Web dashboard interface
[ ] Real-time monitoring mode
[ ] Comparison with DEV.to averages
[ ] Best time to post analysis
[ ] Content recommendation engine
[ ] Integration with other platforms
📄 License
MIT License - feel free to use for personal or commercial projects.
🙏 Acknowledgments
Built by @GnomeMan4201 - Security researcher who got tired of not having proper analytics.
🔗 Links
My DEV.to Profile
Report Issues
Feature Requests
⭐ Found this useful? Give it a star and share with fellow DEV.to writers!
📝 Have suggestions? Open an issue or submit a PR!
