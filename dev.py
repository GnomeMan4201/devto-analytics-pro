#!/usr/bin/env python3
"""
DEV.to Analytics Pro - Advanced analytics for your DEV.to articles
Author: GnomeMan4201
"""

import requests
import argparse
import json
import csv
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict

class DevToAnalytics:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dev.to/api"
        self.headers = {"api-key": api_key}
        self.articles = []
        
    def fetch_articles(self):
        """Fetch all published articles"""
        print("🔄 Fetching your Dev.to articles...")
        response = requests.get(
            f"{self.base_url}/articles/me/all",
            headers=self.headers
        )
        
        if response.status_code == 200:
            self.articles = response.json()
            print(f"✅ Loaded {len(self.articles)} articles\n")
        else:
            print(f"❌ Error: {response.status_code}")
            exit(1)
    
    def filter_by_date(self, days: int = None):
        """Filter articles by date range"""
        if not days:
            return self.articles
            
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        filtered = []
        
        for article in self.articles:
            # Parse published date and make timezone-aware
            pub_date_str = article['published_at'].replace('Z', '+00:00')
            pub_date = datetime.fromisoformat(pub_date_str)
            
            if pub_date >= cutoff:
                filtered.append(article)
        
        return filtered
    
    def calculate_engagement_rate(self, article: Dict) -> float:
        """Calculate engagement rate (reactions + comments) / views * 100"""
        views = article.get('page_views_count', 0)
        if views == 0:
            return 0.0
        reactions = article.get('public_reactions_count', 0)
        comments = article.get('comments_count', 0)
        return ((reactions + comments) / views) * 100
    
    def overview(self, days: int = None):
        """Display overview statistics"""
        articles = self.filter_by_date(days)
        
        if not articles:
            print("❌ No articles found in this time period")
            return
        
        total_views = sum(a.get('page_views_count', 0) for a in articles)
        total_reactions = sum(a.get('public_reactions_count', 0) for a in articles)
        total_comments = sum(a.get('comments_count', 0) for a in articles)
        avg_views = total_views / len(articles) if articles else 0
        
        # Calculate average engagement rate
        total_engagement = sum(self.calculate_engagement_rate(a) for a in articles)
        avg_engagement = total_engagement / len(articles) if articles else 0
        
        time_period = f"last {days} days" if days else "all time"
        
        print(f"\n{'='*60}")
        print(f"📊 DEV.TO ANALYTICS OVERVIEW ({time_period})")
        print(f"{'='*60}")
        print(f"📝 Total Articles:      {len(articles)}")
        print(f"👀 Total Views:         {total_views:,}")
        print(f"❤️  Total Reactions:     {total_reactions}")
        print(f"💬 Total Comments:      {total_comments}")
        print(f"📈 Avg Views/Article:   {avg_views:.0f}")
        print(f"🎯 Engagement Rate:     {avg_engagement:.2f}%")
        print(f"{'='*60}\n")
    
    def top_articles(self, n: int = 10, sort_by: str = 'views', days: int = None):
        """Show top N articles"""
        articles = self.filter_by_date(days)
        
        sort_key = {
            'views': lambda a: a.get('page_views_count', 0),
            'reactions': lambda a: a.get('public_reactions_count', 0),
            'comments': lambda a: a.get('comments_count', 0),
            'engagement': lambda a: self.calculate_engagement_rate(a)
        }
        
        sorted_articles = sorted(articles, key=sort_key[sort_by], reverse=True)[:n]
        
        print(f"\n🏆 TOP {n} ARTICLES (by {sort_by})")
        print("="*100)
        
        for i, article in enumerate(sorted_articles, 1):
            title = article['title'][:70]
            views = article.get('page_views_count', 0)
            reactions = article.get('public_reactions_count', 0)
            comments = article.get('comments_count', 0)
            engagement = self.calculate_engagement_rate(article)
            url = article['url']
            published = article['published_at'][:10]
            
            print(f"\n{i}. {title}")
            print(f"   👀 Views: {views} | ❤️  Reactions: {reactions} | 💬 Comments: {comments} | 🎯 Engagement: {engagement:.2f}%")
            print(f"   🔗 {url}")
            print(f"   📅 Published: {published}")
    
    def tag_analysis(self, days: int = None):
        """Analyze performance by tags"""
        articles = self.filter_by_date(days)
        tag_stats = defaultdict(lambda: {
            'count': 0, 
            'views': 0, 
            'reactions': 0, 
            'comments': 0
        })
        
        for article in articles:
            tags = article.get('tag_list', [])
            views = article.get('page_views_count', 0)
            reactions = article.get('public_reactions_count', 0)
            comments = article.get('comments_count', 0)
            
            for tag in tags:
                tag_stats[tag]['count'] += 1
                tag_stats[tag]['views'] += views
                tag_stats[tag]['reactions'] += reactions
                tag_stats[tag]['comments'] += comments
        
        # Sort by total views
        sorted_tags = sorted(
            tag_stats.items(), 
            key=lambda x: x[1]['views'], 
            reverse=True
        )
        
        print(f"\n🏷️  TAG PERFORMANCE ANALYSIS")
        print("="*100)
        print(f"{'Tag':<20} {'Articles':<10} {'Total Views':<15} {'Avg Views':<12} {'Reactions':<12} {'Comments'}")
        print("-"*100)
        
        for tag, stats in sorted_tags:
            avg_views = stats['views'] / stats['count'] if stats['count'] > 0 else 0
            print(f"{tag:<20} {stats['count']:<10} {stats['views']:<15} {avg_views:<12.0f} {stats['reactions']:<12} {stats['comments']}")
    
    def reading_time_analysis(self, days: int = None):
        """Analyze performance by reading time"""
        articles = self.filter_by_date(days)
        
        # Group by reading time ranges
        time_ranges = {
            '0-3 min': {'articles': [], 'range': (0, 3)},
            '4-5 min': {'articles': [], 'range': (4, 5)},
            '6-10 min': {'articles': [], 'range': (6, 10)},
            '11-15 min': {'articles': [], 'range': (11, 15)},
            '16+ min': {'articles': [], 'range': (16, 999)}
        }
        
        for article in articles:
            reading_time = article.get('reading_time_minutes', 0)
            for range_name, range_data in time_ranges.items():
                min_time, max_time = range_data['range']
                if min_time <= reading_time <= max_time:
                    range_data['articles'].append(article)
                    break
        
        print(f"\n📚 READING TIME ANALYSIS")
        print("="*80)
        print(f"{'Time Range':<15} {'Articles':<10} {'Avg Views':<15} {'Avg Reactions'}")
        print("-"*80)
        
        for range_name, range_data in time_ranges.items():
            articles_in_range = range_data['articles']
            if not articles_in_range:
                continue
                
            avg_views = sum(a.get('page_views_count', 0) for a in articles_in_range) / len(articles_in_range)
            avg_reactions = sum(a.get('public_reactions_count', 0) for a in articles_in_range) / len(articles_in_range)
            
            print(f"{range_name:<15} {len(articles_in_range):<10} {avg_views:<15.0f} {avg_reactions:.1f}")
    
    def growth_trends(self):
        """Show growth trends by month"""
        monthly_stats = defaultdict(lambda: {
            'articles': 0,
            'views': 0,
            'reactions': 0,
            'comments': 0
        })
        
        for article in self.articles:
            pub_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
            month_key = pub_date.strftime('%Y-%m')
            
            monthly_stats[month_key]['articles'] += 1
            monthly_stats[month_key]['views'] += article.get('page_views_count', 0)
            monthly_stats[month_key]['reactions'] += article.get('public_reactions_count', 0)
            monthly_stats[month_key]['comments'] += article.get('comments_count', 0)
        
        sorted_months = sorted(monthly_stats.items())
        
        print(f"\n📈 GROWTH TREND (Last 12 Months)")
        print("="*80)
        print(f"{'Month':<15} {'Articles':<10} {'Total Views':<15} {'Total Reactions'}")
        print("-"*80)
        
        for month, stats in sorted_months[-12:]:
            print(f"{month:<15} {stats['articles']:<10} {stats['views']:<15} {stats['reactions']}")
    
    def underperformers(self, days: int = 30):
        """Find underperforming articles"""
        articles = self.filter_by_date(days)
        
        if not articles:
            print(f"❌ No articles published in the last {days} days")
            return
        
        avg_views = sum(a.get('page_views_count', 0) for a in articles) / len(articles)
        avg_engagement = sum(self.calculate_engagement_rate(a) for a in articles) / len(articles)
        
        underperformers = [
            a for a in articles 
            if a.get('page_views_count', 0) < avg_views * 0.5 
            or self.calculate_engagement_rate(a) < avg_engagement * 0.5
        ]
        
        if not underperformers:
            print(f"\n✅ No significantly underperforming articles in the last {days} days!")
            return
        
        print(f"\n⚠️  UNDERPERFORMING ARTICLES (Last {days} days)")
        print("="*100)
        print(f"Articles with <50% of average views ({avg_views:.0f}) or engagement ({avg_engagement:.2f}%)\n")
        
        for article in underperformers:
            title = article['title'][:70]
            views = article.get('page_views_count', 0)
            engagement = self.calculate_engagement_rate(article)
            
            print(f"📉 {title}")
            print(f"   Views: {views} (avg: {avg_views:.0f}) | Engagement: {engagement:.2f}% (avg: {avg_engagement:.2f}%)")
            print(f"   🔗 {article['url']}\n")
    
    def export_json(self, filename: str, days: int = None):
        """Export data to JSON"""
        articles = self.filter_by_date(days)
        
        export_data = {
            'exported_at': datetime.now(timezone.utc).isoformat(),
            'total_articles': len(articles),
            'total_views': sum(a.get('page_views_count', 0) for a in articles),
            'total_reactions': sum(a.get('public_reactions_count', 0) for a in articles),
            'articles': articles
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Data exported to {filename}")
    
    def export_csv(self, filename: str, days: int = None):
        """Export data to CSV"""
        articles = self.filter_by_date(days)
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Title', 'URL', 'Published', 'Views', 'Reactions', 
                'Comments', 'Engagement %', 'Reading Time', 'Tags'
            ])
            
            for article in articles:
                writer.writerow([
                    article['title'],
                    article['url'],
                    article['published_at'][:10],
                    article.get('page_views_count', 0),
                    article.get('public_reactions_count', 0),
                    article.get('comments_count', 0),
                    f"{self.calculate_engagement_rate(article):.2f}",
                    article.get('reading_time_minutes', 0),
                    ', '.join(article.get('tag_list', []))
                ])
        
        print(f"✅ Data exported to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Dev.to Analytics CLI - Advanced analytics for your articles',
        epilog='''
Examples:
  # Basic overview
  python dev.py --api-key YOUR_KEY --overview

  # Top 20 articles by engagement
  python dev.py --api-key YOUR_KEY --top 20 --sort engagement

  # Last 30 days overview
  python dev.py --api-key YOUR_KEY --overview --days 30

  # Tag analysis for last 90 days
  python dev.py --api-key YOUR_KEY --tags --days 90

  # Export to CSV
  python dev.py --api-key YOUR_KEY --export-csv analytics.csv

  # Full report
  python dev.py --api-key YOUR_KEY --full-report
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--api-key', required=True, help='Your Dev.to API key')
    parser.add_argument('--overview', action='store_true', help='Show overview statistics')
    parser.add_argument('--top', type=int, metavar='N', help='Show top N articles')
    parser.add_argument('--sort', choices=['views', 'reactions', 'comments', 'engagement'],
                       default='views', help='Sort criteria for top articles')
    parser.add_argument('--tags', action='store_true', help='Show tag analysis')
    parser.add_argument('--reading-time', action='store_true', help='Show reading time analysis')
    parser.add_argument('--growth', action='store_true', help='Show growth trends')
    parser.add_argument('--underperformers', action='store_true', help='Find underperforming articles')
    parser.add_argument('--days', type=int, help='Filter by last N days')
    parser.add_argument('--export-json', metavar='FILE', help='Export data to JSON file')
    parser.add_argument('--export-csv', metavar='FILE', help='Export data to CSV file')
    parser.add_argument('--full-report', action='store_true', help='Generate full analytics report')
    
    args = parser.parse_args()
    
    analytics = DevToAnalytics(args.api_key)
    analytics.fetch_articles()
    
    # Execute requested analyses
    if args.full_report:
        analytics.overview(args.days)
        analytics.top_articles(10, args.sort, args.days)
        analytics.tag_analysis(args.days)
        analytics.reading_time_analysis(args.days)
        analytics.growth_trends()
        analytics.underperformers(args.days or 30)
    else:
        if args.overview:
            analytics.overview(args.days)
        if args.top:
            analytics.top_articles(args.top, args.sort, args.days)
        if args.tags:
            analytics.tag_analysis(args.days)
        if args.reading_time:
            analytics.reading_time_analysis(args.days)
        if args.growth:
            analytics.growth_trends()
        if args.underperformers:
            analytics.underperformers(args.days or 30)
    
    if args.export_json:
        analytics.export_json(args.export_json, args.days)
    if args.export_csv:
        analytics.export_csv(args.export_csv, args.days)


if __name__ == "__main__":
    main()
