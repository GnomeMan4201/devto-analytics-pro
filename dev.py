#!/usr/bin/env python3
"""
DEV.to Analytics Pro - Advanced analytics for your DEV.to articles
Author: GnomeMan4201
Contributors: Pascal CESCATO (@pcescato)
"""

import requests
import argparse
import json
import csv
import re
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Optional, Tuple

class DevToAnalytics:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dev.to/api"
        self.headers = {"api-key": api_key}
        self.articles = []
        self._followers_cache = None
        self._own_username = None

    def _get_own_username(self) -> str:
        """Fetch the authenticated user's username for self-filtering."""
        if self._own_username:
            return self._own_username
        try:
            r = requests.get(f"{self.base_url}/users/me",
                             headers=self.headers, timeout=10)
            if r.status_code == 200:
                self._own_username = r.json().get('username', '').lower()
        except Exception:
            pass
        return self._own_username or ''

    def fetch_articles(self):
        """Fetch all published articles"""
        print("🔄 Fetching your Dev.to articles...")
        try:
            response = requests.get(
                f"{self.base_url}/articles/me/all",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                self.articles = response.json()
                print(f"✅ Loaded {len(self.articles)} articles\n")
            elif response.status_code == 401:
                print("❌ Error: Invalid API key (401 Unauthorized)")
                print("Please check your API key at https://dev.to/settings/extensions")
                exit(1)
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                exit(1)
        except requests.exceptions.Timeout:
            print("❌ Error: Request timed out.")
            exit(1)
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: Failed to connect to DEV.to API\nDetails: {str(e)}")
            exit(1)

    def fetch_followers(self) -> List[Dict]:
        """Fetch follower list (paginated)"""
        if self._followers_cache is not None:
            return self._followers_cache
        followers = []
        page = 1
        print("🔄 Fetching follower data...")
        while True:
            try:
                r = requests.get(
                    f"{self.base_url}/followers/users",
                    headers=self.headers,
                    params={"per_page": 1000, "page": page},
                    timeout=10
                )
                if r.status_code != 200:
                    break
                batch = r.json()
                if not batch:
                    break
                followers.extend(batch)
                if len(batch) < 1000:
                    break
                page += 1
            except Exception:
                break
        self._followers_cache = followers
        print(f"✅ Loaded {len(followers)} followers\n")
        return followers

    def filter_by_date(self, days: int = None) -> List[Dict]:
        """Filter articles by date range"""
        if not days:
            return self.articles
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        filtered = []
        for article in self.articles:
            if not article.get('published_at'):
                continue
            pub_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
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

    # ─── EXISTING METHODS ────────────────────────────────────────────────────

    def overview(self, days: int = None):
        articles = self.filter_by_date(days)
        if not articles:
            print("❌ No articles found in this time period")
            return
        total_views = sum(a.get('page_views_count', 0) for a in articles)
        total_reactions = sum(a.get('public_reactions_count', 0) for a in articles)
        total_comments = sum(a.get('comments_count', 0) for a in articles)
        avg_views = total_views / len(articles) if articles else 0
        avg_engagement = sum(self.calculate_engagement_rate(a) for a in articles) / len(articles) if articles else 0
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
        articles = self.filter_by_date(days)
        if not articles:
            print("❌ No articles found in this time period")
            return
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
            published = article['published_at'][:10] if article['published_at'] else "Unpublished"
            print(f"\n{i}. {title}")
            print(f"   👀 Views: {views} | ❤️  Reactions: {reactions} | 💬 Comments: {comments} | 🎯 Engagement: {engagement:.2f}%")
            print(f"   🔗 {article['url']}")
            print(f"   📅 Published: {published}")

    def tag_analysis(self, days: int = None):
        articles = self.filter_by_date(days)
        if not articles:
            print("❌ No articles found in this time period")
            return
        tag_stats = defaultdict(lambda: {'count': 0, 'views': 0, 'reactions': 0, 'comments': 0})
        for article in articles:
            for tag in article.get('tag_list', []):
                tag_stats[tag]['count'] += 1
                tag_stats[tag]['views'] += article.get('page_views_count', 0)
                tag_stats[tag]['reactions'] += article.get('public_reactions_count', 0)
                tag_stats[tag]['comments'] += article.get('comments_count', 0)
        if not tag_stats:
            print("❌ No tags found")
            return
        sorted_tags = sorted(tag_stats.items(), key=lambda x: x[1]['views'], reverse=True)
        print(f"\n🏷️  TAG PERFORMANCE ANALYSIS")
        print("="*100)
        print(f"{'Tag':<20} {'Articles':<10} {'Total Views':<15} {'Avg Views':<12} {'Reactions':<12} {'Comments'}")
        print("-"*100)
        for tag, stats in sorted_tags:
            avg_views = stats['views'] / stats['count'] if stats['count'] > 0 else 0
            print(f"{tag:<20} {stats['count']:<10} {stats['views']:<15} {avg_views:<12.0f} {stats['reactions']:<12} {stats['comments']}")

    def reading_time_analysis(self, days: int = None):
        articles = self.filter_by_date(days)
        if not articles:
            print("❌ No articles found")
            return
        time_ranges = {
            '0-3 min':  {'articles': [], 'range': (0, 3)},
            '4-5 min':  {'articles': [], 'range': (4, 5)},
            '6-10 min': {'articles': [], 'range': (6, 10)},
            '11-15 min':{'articles': [], 'range': (11, 15)},
            '16+ min':  {'articles': [], 'range': (16, 999)}
        }
        for article in articles:
            rt = article.get('reading_time_minutes', 0)
            for rn, rd in time_ranges.items():
                if rd['range'][0] <= rt <= rd['range'][1]:
                    rd['articles'].append(article)
                    break
        print(f"\n📚 READING TIME ANALYSIS")
        print("="*80)
        print(f"{'Time Range':<15} {'Articles':<10} {'Avg Views':<15} {'Avg Reactions'}")
        print("-"*80)
        for rn, rd in time_ranges.items():
            if not rd['articles']:
                continue
            avg_v = sum(a.get('page_views_count', 0) for a in rd['articles']) / len(rd['articles'])
            avg_r = sum(a.get('public_reactions_count', 0) for a in rd['articles']) / len(rd['articles'])
            print(f"{rn:<15} {len(rd['articles']):<10} {avg_v:<15.0f} {avg_r:.1f}")

    def growth_trends(self):
        if not self.articles:
            print("❌ No articles found")
            return
        monthly = defaultdict(lambda: {'articles': 0, 'views': 0, 'reactions': 0, 'comments': 0})
        for article in self.articles:
            if not article.get('published_at'):
                continue
            pub = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
            k = pub.strftime('%Y-%m')
            monthly[k]['articles'] += 1
            monthly[k]['views'] += article.get('page_views_count', 0)
            monthly[k]['reactions'] += article.get('public_reactions_count', 0)
            monthly[k]['comments'] += article.get('comments_count', 0)
        if not monthly:
            print("❌ No published articles with dates found")
            return
        print(f"\n📈 GROWTH TREND (Last 12 Months)")
        print("="*80)
        print(f"{'Month':<15} {'Articles':<10} {'Total Views':<15} {'Total Reactions'}")
        print("-"*80)
        for month, stats in sorted(monthly.items())[-12:]:
            print(f"{month:<15} {stats['articles']:<10} {stats['views']:<15} {stats['reactions']}")

    def underperformers(self, days: int = 30):
        articles = self.filter_by_date(days)
        if not articles or len(articles) < 2:
            print(f"ℹ️  Need at least 2 articles in the last {days} days")
            return
        avg_views = sum(a.get('page_views_count', 0) for a in articles) / len(articles)
        avg_eng = sum(self.calculate_engagement_rate(a) for a in articles) / len(articles)
        under = [a for a in articles
                 if a.get('page_views_count', 0) < avg_views * 0.5
                 and self.calculate_engagement_rate(a) < avg_eng * 0.5]
        if not under:
            print(f"\n✅ No significantly underperforming articles in the last {days} days!")
            return
        print(f"\n⚠️  UNDERPERFORMING ARTICLES (Last {days} days)")
        print("="*100)
        print(f"Articles with <50% of avg views ({avg_views:.0f}) AND <50% of avg engagement ({avg_eng:.2f}%)\n")
        for article in under:
            title = article['title'][:70]
            views = article.get('page_views_count', 0)
            eng = self.calculate_engagement_rate(article)
            print(f"📉 {title}")
            print(f"   Views: {views} (avg: {avg_views:.0f}) | Engagement: {eng:.2f}% (avg: {avg_eng:.2f}%)")
            print(f"   🔗 {article['url']}\n")

    # ─── NEW METHODS ─────────────────────────────────────────────────────────

    def series_analysis(self):
        """
        Detect and analyse multi-part article series.
        Heuristics: shared title prefix before a number/part marker, or
        articles that share all but the last word of their slug.
        Groups are sorted by publication date; metrics are compared across parts.
        """
        if not self.articles:
            print("❌ No articles found")
            return

        PART_RE = re.compile(
            r'[\s\-–—:]+(?:part|pt|episode|ep|vol|volume|chapter|ch|#)\s*(\d+)\b',
            re.IGNORECASE
        )
        NUM_SUFFIX_RE = re.compile(r'[\s\-–]+(\d+)\s*$')

        def series_key(title: str) -> Optional[str]:
            m = PART_RE.search(title)
            if m:
                return PART_RE.sub('', title).strip().lower()
            m2 = NUM_SUFFIX_RE.search(title)
            if m2:
                return NUM_SUFFIX_RE.sub('', title).strip().lower()
            return None

        groups: Dict[str, List[Dict]] = defaultdict(list)
        solo = []
        for article in self.articles:
            key = series_key(article.get('title', ''))
            if key:
                groups[key].append(article)
            else:
                solo.append(article)

        series_groups = {k: sorted(v, key=lambda a: a.get('published_at') or '')
                         for k, v in groups.items() if len(v) > 1}

        if not series_groups:
            print("\nℹ️  No multi-part series detected in your articles.")
            print("    (Heuristic: looks for 'Part N', 'Ep N', 'Vol N', or trailing number in title)")
            return

        print(f"\n📚 SERIES PERFORMANCE ANALYSIS")
        print(f"    Detected {len(series_groups)} series across {sum(len(v) for v in series_groups.values())} articles\n")
        print("="*110)

        for series_name, parts in sorted(series_groups.items()):
            total_views   = sum(a.get('page_views_count', 0) for a in parts)
            total_reacts  = sum(a.get('public_reactions_count', 0) for a in parts)
            total_comments= sum(a.get('comments_count', 0) for a in parts)
            avg_eng       = sum(self.calculate_engagement_rate(a) for a in parts) / len(parts)

            # Drop-off: view ratio between first and last part
            first_views = parts[0].get('page_views_count', 0)
            last_views  = parts[-1].get('page_views_count', 0)
            dropoff = ((first_views - last_views) / first_views * 100) if first_views > 0 else 0

            display_name = series_name.title()[:60]
            print(f"\n  📖 {display_name}  ({len(parts)} parts)")
            print(f"     Total views: {total_views:,}  |  Reactions: {total_reacts}  |  "
                  f"Comments: {total_comments}  |  Avg engagement: {avg_eng:.2f}%")
            if len(parts) > 1:
                arrow = "📉" if dropoff > 20 else "📈" if dropoff < 0 else "➡️"
                print(f"     {arrow}  Reader retention: {100 - dropoff:.0f}%  "
                      f"(part 1: {first_views:,} views → part {len(parts)}: {last_views:,} views)")
            print()

            for i, part in enumerate(parts, 1):
                title   = part['title'][:65]
                views   = part.get('page_views_count', 0)
                reacts  = part.get('public_reactions_count', 0)
                eng     = self.calculate_engagement_rate(part)
                pub     = part['published_at'][:10] if part.get('published_at') else '—'
                print(f"     {i:>2}. {title:<65}  {views:>6} views  {reacts:>4} ❤️   {eng:>5.2f}%  {pub}")

        print("\n" + "="*110)
        print(f"\n  Standalone articles (not part of a detected series): {len(solo)}")

    def follower_correlation(self):
        """
        Correlate follower growth events with publish dates.
        DEV.to API returns follower list with joined_at timestamps.
        We bin followers by week and overlay publish events to surface
        which articles appear to have driven follow spikes.
        """
        followers = self.fetch_followers()
        if not followers:
            print("❌ No follower data available (check API key scope)")
            return
        if not self.articles:
            print("❌ No articles loaded")
            return

        # Bin followers by ISO week
        week_counts: Dict[str, int] = defaultdict(int)
        for f in followers:
            joined = f.get('created_at') or f.get('joined_at') or ''
            if not joined:
                continue
            try:
                dt = datetime.fromisoformat(joined.replace('Z', '+00:00'))
                week_key = dt.strftime('%G-W%V')  # ISO week
                week_counts[week_key] += 1
            except ValueError:
                continue

        if not week_counts:
            print("ℹ️  Follower timestamps not available in API response.")
            print("    DEV.to may not expose joined_at for all followers.")
            return

        # Map publish events to weeks
        publish_weeks: Dict[str, List[str]] = defaultdict(list)
        for article in self.articles:
            if not article.get('published_at'):
                continue
            dt = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
            wk = dt.strftime('%G-W%V')
            publish_weeks[wk].append(article['title'][:50])

        all_weeks = sorted(set(list(week_counts.keys()) + list(publish_weeks.keys())))
        if not all_weeks:
            print("❌ No temporal data to correlate")
            return

        max_followers = max(week_counts.values()) if week_counts else 1
        bar_width = 40

        print(f"\n👥 FOLLOWER GROWTH × PUBLISH EVENT CORRELATION")
        print(f"   Total followers tracked: {len(followers)}")
        print("="*90)
        print(f"{'Week':<12} {'New followers':<16} {'Bar':<{bar_width+2}} Articles published")
        print("-"*90)

        for week in all_weeks[-26:]:  # last 26 weeks
            count = week_counts.get(week, 0)
            bar_len = int(count / max_followers * bar_width) if max_followers else 0
            bar = '█' * bar_len
            articles_str = '; '.join(publish_weeks.get(week, []))
            articles_str = articles_str[:35] + '…' if len(articles_str) > 35 else articles_str
            marker = '⬅ 📝' if articles_str else ''
            print(f"{week:<12} {count:<16} {bar:<{bar_width+2}} {articles_str} {marker}")

        # Surface top correlation: weeks with both high followers AND a publish event
        print(f"\n  🔍 Highest-follower weeks with a publish event:")
        correlated = [(w, week_counts[w], publish_weeks[w])
                      for w in all_weeks if w in week_counts and w in publish_weeks]
        correlated.sort(key=lambda x: x[1], reverse=True)
        for week, count, titles in correlated[:5]:
            print(f"     {week}: +{count} followers — \"{titles[0]}\"")

    def publish_time_heatmap(self):
        """
        Build a day-of-week × hour-of-day heatmap showing average views
        for articles published at each time slot.
        """
        if not self.articles:
            print("❌ No articles loaded")
            return

        DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        # slot_data[day][hour] = list of view counts
        slot_data: Dict[int, Dict[int, List[int]]] = {d: defaultdict(list) for d in range(7)}

        for article in self.articles:
            if not article.get('published_at'):
                continue
            dt = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
            day = dt.weekday()   # 0=Mon
            hour = dt.hour
            views = article.get('page_views_count', 0)
            slot_data[day][hour].append(views)

        # Build avg matrix
        matrix: Dict[int, Dict[int, float]] = {}
        for day in range(7):
            matrix[day] = {}
            for hour in range(24):
                vals = slot_data[day][hour]
                matrix[day][hour] = sum(vals) / len(vals) if vals else 0.0

        # Find global max for normalisation
        all_vals = [matrix[d][h] for d in range(7) for h in range(24) if matrix[d][h] > 0]
        global_max = max(all_vals) if all_vals else 1

        BLOCKS = ' ░▒▓█'

        print(f"\n⏰ OPTIMAL PUBLISH TIME HEATMAP")
        print(f"   Based on {len(self.articles)} articles — avg views per day/hour slot")
        print(f"   Scale: {' '.join(BLOCKS)} (low → high avg views)\n")

        # Hour header
        hour_header = '     ' + ''.join(f"{h:02d}" for h in range(0, 24, 2))
        print(hour_header)
        print('     ' + '--' * 12)

        for day in range(7):
            row = f"{DAYS[day]}  |"
            for hour in range(24):
                val = matrix[day][hour]
                if val == 0:
                    row += '·'
                else:
                    level = int(val / global_max * (len(BLOCKS) - 1))
                    row += BLOCKS[level]
            row += '|'
            print(row)

        print('     ' + '--' * 12)

        # Best slots
        ranked = []
        for day in range(7):
            for hour in range(24):
                if matrix[day][hour] > 0:
                    ranked.append((matrix[day][hour], day, hour, len(slot_data[day][hour])))
        ranked.sort(reverse=True)

        print(f"\n  🏆 Top 5 publish slots by avg views:")
        for avg_v, day, hour, count in ranked[:5]:
            print(f"     {DAYS[day]} {hour:02d}:00  →  {avg_v:,.0f} avg views  ({count} article{'s' if count!=1 else ''})")

        if not ranked:
            print("  ℹ️  Not enough publish time data (need articles with timestamps)")

    def cross_platform_reach(self):
        """
        Estimate cross-platform reach by:
        1. Scanning article bodies/canonical URLs for cross-post markers
        2. Summarising DEV.to native reach with platform distribution estimate
        3. Flagging canonical_url pointing elsewhere (syndicated from another platform)
        """
        if not self.articles:
            print("❌ No articles loaded")
            return

        PLATFORM_SIGNALS = {
            'Medium':       ['medium.com', 'towardsdatascience.com', 'betterprogramming.pub'],
            'Hashnode':     ['hashnode.com', 'hashnode.dev'],
            'Substack':     ['substack.com'],
            'Personal blog':['github.io', 'netlify.app', 'vercel.app'],
            'LinkedIn':     ['linkedin.com/pulse'],
        }

        canonical_counts: Dict[str, int] = defaultdict(int)
        cross_posted: List[Dict] = []
        devto_native: List[Dict] = []

        for article in self.articles:
            canon = article.get('canonical_url') or ''
            url   = article.get('url') or ''

            # If canonical points away from DEV.to it's syndicated FROM another platform
            if canon and 'dev.to' not in canon and canon != url:
                matched = False
                for platform, signals in PLATFORM_SIGNALS.items():
                    if any(s in canon for s in signals):
                        canonical_counts[platform] += 1
                        matched = True
                        break
                if not matched:
                    canonical_counts['Other'] += 1
                cross_posted.append({**article, '_source_platform': canon})
            else:
                devto_native.append(article)

        total_views     = sum(a.get('page_views_count', 0) for a in self.articles)
        native_views    = sum(a.get('page_views_count', 0) for a in devto_native)
        syndicated_views= sum(a.get('page_views_count', 0) for a in cross_posted)

        print(f"\n🌐 CROSS-PLATFORM REACH ANALYSIS")
        print("="*80)
        print(f"  Total articles:          {len(self.articles)}")
        print(f"  DEV.to native:           {len(devto_native)} articles  ({native_views:,} views)")
        print(f"  Syndicated (from others):{len(cross_posted)} articles  ({syndicated_views:,} views)")
        print()

        if canonical_counts:
            print(f"  Source platform breakdown:")
            for platform, count in sorted(canonical_counts.items(), key=lambda x: -x[1]):
                print(f"     {platform:<20} {count} article{'s' if count != 1 else ''}")
            print()

        # Engagement comparison: native vs syndicated
        if devto_native and cross_posted:
            native_eng = sum(self.calculate_engagement_rate(a) for a in devto_native) / len(devto_native)
            syndi_eng  = sum(self.calculate_engagement_rate(a) for a in cross_posted) / len(cross_posted)
            print(f"  Engagement rate comparison:")
            print(f"     Native:     {native_eng:.2f}%")
            print(f"     Syndicated: {syndi_eng:.2f}%")
            winner = "native" if native_eng > syndi_eng else "syndicated"
            print(f"     → {winner.title()} content drives higher engagement on DEV.to")
            print()

        # Reach estimate: DEV.to views + rough multiplier for original platform
        # We conservatively assume original platform has ~0.5–2× DEV.to view count
        print(f"  Estimated total reach (conservative):")
        print(f"     DEV.to views:              {total_views:,}")
        if cross_posted:
            est_low  = syndicated_views * 0.5
            est_high = syndicated_views * 2.0
            print(f"     Estimated upstream views:  {est_low:,.0f} – {est_high:,.0f}")
            print(f"     Combined reach estimate:   {total_views + est_low:,.0f} – {total_views + est_high:,.0f}")
        else:
            print(f"     No syndicated articles detected — all reach is DEV.to native")

        if cross_posted:
            print(f"\n  Syndicated articles:")
            for a in sorted(cross_posted, key=lambda x: x.get('page_views_count', 0), reverse=True)[:10]:
                title = a['title'][:60]
                views = a.get('page_views_count', 0)
                src   = a['_source_platform'][:50]
                print(f"     {views:>6} views  {title:<60}  ← {src}")

        print()

    # ─── AUDIENCE METHODS ────────────────────────────────────────────────────

    def fetch_comments(self) -> Dict[int, List[Dict]]:
        """
        Fetch all comments across all articles.
        Returns dict: article_id → list of comment dicts.
        DEV.to /api/comments?a_id={id} returns a tree; we flatten it.
        """
        if not self.articles:
            return {}

        print("🔄 Fetching comments across all articles...")
        all_comments: Dict[int, List[Dict]] = {}
        total = 0

        def flatten(nodes: List[Dict], article_id: int) -> List[Dict]:
            """Recursively flatten threaded comment tree."""
            flat = []
            for node in nodes:
                flat.append({
                    'id':         node.get('id'),
                    'article_id': article_id,
                    'username':   node.get('user', {}).get('username', ''),
                    'name':       node.get('user', {}).get('name', ''),
                    'created_at': node.get('created_at', ''),
                    'body_html':  node.get('body_html', ''),
                })
                if node.get('children'):
                    flat.extend(flatten(node['children'], article_id))
            return flat

        for article in self.articles:
            aid = article.get('id')
            if not aid:
                continue
            try:
                r = requests.get(
                    f"{self.base_url}/comments",
                    headers=self.headers,
                    params={'a_id': aid},
                    timeout=10
                )
                if r.status_code == 200:
                    flat = flatten(r.json(), aid)
                    all_comments[aid] = flat
                    total += len(flat)
            except Exception:
                pass

        print(f"✅ Loaded {total} comments across {len(all_comments)} articles\n")
        return all_comments

    def commenters(self):
        """
        Rank commenters by frequency across all your articles.
        Shows: comment count, articles commented on, first/last comment date,
        and which articles they engage with most.
        """
        comments_by_article = self.fetch_comments()
        if not comments_by_article:
            print("❌ No comments found")
            return

        # Build article_id → title map
        id_to_title = {a['id']: a['title'] for a in self.articles if a.get('id')}

        # Aggregate per commenter — exclude article owner's own replies
        OWNER = self._get_own_username()
        commenter_stats: Dict[str, Dict] = {}
        for aid, comments in comments_by_article.items():
            article_title = id_to_title.get(aid, f'article {aid}')
            for c in comments:
                u = c['username']
                if not u:
                    continue
                if OWNER and u.lower() == OWNER:
                    continue  # skip own replies
                if u not in commenter_stats:
                    commenter_stats[u] = {
                        'name':      c['name'],
                        'username':  u,
                        'count':     0,
                        'articles':  {},
                        'dates':     [],
                    }
                commenter_stats[u]['count'] += 1
                commenter_stats[u]['articles'][article_title] = \
                    commenter_stats[u]['articles'].get(article_title, 0) + 1
                if c['created_at']:
                    commenter_stats[u]['dates'].append(c['created_at'])

        if not commenter_stats:
            print("❌ No commenter data found")
            return

        ranked = sorted(commenter_stats.values(), key=lambda x: x['count'], reverse=True)

        total_comments = sum(v['count'] for v in ranked)
        print(f"\n💬 COMMENTER ANALYSIS")
        print(f"   {total_comments} total comments from {len(ranked)} unique commenters")
        print("="*100)
        print(f"{'Rank':<6} {'Username':<25} {'Name':<25} {'Comments':<10} {'Articles':<10} {'Top article'}")
        print("-"*100)

        for i, c in enumerate(ranked[:30], 1):
            dates  = sorted(c['dates'])
            first  = dates[0][:10] if dates else '—'
            last   = dates[-1][:10] if dates else '—'
            top_art= max(c['articles'], key=c['articles'].get) if c['articles'] else '—'
            top_art_display = top_art[:45] + '…' if len(top_art) > 45 else top_art
            n_arts = len(c['articles'])
            print(f"{i:<6} @{c['username']:<24} {c['name']:<25} {c['count']:<10} {n_arts:<10} {top_art_display}")

        print()
        print(f"  📅 Commenter tenure (first → most recent comment across all articles):")
        oldest = min((c['dates'][0] for c in ranked if c['dates']), default='—')
        newest = max((c['dates'][-1] for c in ranked if c['dates']), default='—')
        print(f"     Earliest comment: {oldest[:10]}")
        print(f"     Most recent:      {newest[:10]}")
        print()

        # Repeat commenters (commented on 3+ articles)
        loyal = [c for c in ranked if len(c['articles']) >= 3]
        if loyal:
            print(f"  🌟 Power commenters (engaged with 3+ different articles):")
            for c in loyal:
                arts = ', '.join(f'"{t[:30]}"' for t in list(c['articles'].keys())[:3])
                print(f"     @{c['username']} — {c['count']} comments across {len(c['articles'])} articles")
                print(f"       Articles: {arts}")

    def loyal_readers(self):
        """
        Cross-reference commenters with followers to find people who:
        - Follow you AND have commented (confirmed engaged followers)
        - Comment frequently across multiple articles (super-fans)
        - Are early adopters (followed before W46 2025 inflection point)
        """
        followers    = self.fetch_followers()
        comments_by  = self.fetch_comments()

        if not followers:
            print("❌ No follower data")
            return

        follower_usernames = {f.get('username', '').lower(): f for f in followers}

        # Build commenter map
        OWNER_L = self._get_own_username()
        commenter_stats: Dict[str, Dict] = {}
        id_to_title = {a['id']: a['title'] for a in self.articles if a.get('id')}
        for aid, comments in comments_by.items():
            for c in comments:
                u = c['username'].lower()
                if not u:
                    continue
                if OWNER_L and u == OWNER_L:
                    continue  # skip own replies
                if u not in commenter_stats:
                    commenter_stats[u] = {'name': c['name'], 'username': c['username'],
                                          'count': 0, 'articles': set(), 'dates': []}
                commenter_stats[u]['count'] += 1
                commenter_stats[u]['articles'].add(id_to_title.get(aid, str(aid)))
                if c['created_at']:
                    commenter_stats[u]['dates'].append(c['created_at'])

        # Intersection: follows + commented
        both = {u: commenter_stats[u] for u in commenter_stats if u in follower_usernames}

        # Follower join dates for early-adopter detection
        INFLECTION = '2025-11-15'  # Week 46 2025 — first spike

        print(f"\n👥 LOYAL READER ANALYSIS")
        print(f"   {len(followers)} followers · {len(commenter_stats)} unique commenters · "
              f"{len(both)} follow AND comment")
        print("="*100)

        if both:
            print(f"\n  🎯 Followers who also comment (highest-value audience):")
            ranked_both = sorted(both.values(), key=lambda x: x['count'], reverse=True)
            print(f"  {'Username':<25} {'Comments':<10} {'Articles':<10} {'Follower since':<18} {'Early adopter'}")
            print("  " + "-"*80)
            for c in ranked_both[:20]:
                fdata     = follower_usernames.get(c['username'].lower(), {})
                joined    = (fdata.get('created_at') or fdata.get('joined_at') or '')[:10]
                early     = '⭐ YES' if joined and joined < INFLECTION else ''
                n_arts    = len(c['articles'])
                print(f"  @{c['username']:<24} {c['count']:<10} {n_arts:<10} {joined:<18} {early}")
        else:
            print("  ℹ️  No overlap found between follower list and commenters.")
            print("      (DEV.to may not return username in follower API for all accounts)")

        # Pure commenter loyalty (multi-article, non-follower)
        non_follower_commenters = {u: v for u, v in commenter_stats.items()
                                   if u not in follower_usernames and len(v['articles']) >= 2}
        if non_follower_commenters:
            print(f"\n  💡 Engaged commenters who haven't followed yet ({len(non_follower_commenters)}):")
            print(f"     (These are conversion opportunities)")
            for u, c in sorted(non_follower_commenters.items(),
                                key=lambda x: x[1]['count'], reverse=True)[:10]:
                arts = ', '.join(f'"{t[:25]}"' for t in list(c['articles'])[:2])
                print(f"     @{c['username']} — {c['count']} comments, {len(c['articles'])} articles — {arts}")

        # Early adopters: followed before inflection point
        early_adopters = []
        for f in followers:
            joined = (f.get('created_at') or f.get('joined_at') or '')
            if joined and joined[:10] < INFLECTION:
                early_adopters.append(f)

        print(f"\n  ⭐ Early adopters (followed before W46 2025 inflection, {len(early_adopters)} total):")
        for f in early_adopters[:10]:
            joined = (f.get('created_at') or f.get('joined_at') or '')[:10]
            u      = f.get('username', '?')
            is_commenter = '💬 comments' if u.lower() in commenter_stats else ''
            print(f"     @{u:<25} followed {joined}  {is_commenter}")
        if len(early_adopters) > 10:
            print(f"     … and {len(early_adopters)-10} more")

    def insights(self):
        """
        Synthesise all available data into a ranked, actionable intelligence report.
        Covers: content strategy, audience, timing, tags, underperformers, growth trajectory.
        """
        if not self.articles:
            print("❌ No articles loaded")
            return

        articles = self.articles
        total_views    = sum(a.get('page_views_count', 0) for a in articles)
        total_reactions= sum(a.get('public_reactions_count', 0) for a in articles)
        total_comments = sum(a.get('comments_count', 0) for a in articles)
        avg_views      = total_views / len(articles) if articles else 0
        avg_eng        = sum(self.calculate_engagement_rate(a) for a in articles) / len(articles) if articles else 0

        # Growth trajectory — last 3 months vs prior 3 months
        now = datetime.now(timezone.utc)
        def month_views(months_ago_start, months_ago_end):
            start = now - timedelta(days=30*months_ago_start)
            end   = now - timedelta(days=30*months_ago_end)
            return sum(a.get('page_views_count',0) for a in articles
                       if a.get('published_at') and
                       end <= datetime.fromisoformat(a['published_at'].replace('Z','+00:00')) <= start)

        recent_views = month_views(3, 0)
        prior_views  = month_views(6, 3)
        trajectory   = ((recent_views - prior_views) / prior_views * 100) if prior_views else 0

        # Top performing content by engagement
        top_eng = sorted(articles, key=self.calculate_engagement_rate, reverse=True)[:3]
        top_views = sorted(articles, key=lambda a: a.get('page_views_count',0), reverse=True)[:3]

        # Tag intelligence
        tag_stats: Dict[str, Dict] = {}
        for a in articles:
            for t in a.get('tag_list', []):
                if t not in tag_stats:
                    tag_stats[t] = {'count': 0, 'views': 0, 'eng_sum': 0}
                tag_stats[t]['count'] += 1
                tag_stats[t]['views'] += a.get('page_views_count', 0)
                tag_stats[t]['eng_sum'] += self.calculate_engagement_rate(a)
        # Tags with avg views > overall avg and used more than once
        breakout_tags = [(t, s) for t, s in tag_stats.items()
                         if s['count'] >= 2 and s['views']/s['count'] > avg_views * 1.3]
        breakout_tags.sort(key=lambda x: x[1]['views']/x[1]['count'], reverse=True)

        underused_high = [(t, s) for t, s in tag_stats.items()
                          if s['count'] == 1 and s['views'] > avg_views * 2]
        underused_high.sort(key=lambda x: x[1]['views'], reverse=True)

        # Underperformers
        under = [a for a in articles
                 if a.get('page_views_count',0) < avg_views * 0.5
                 and self.calculate_engagement_rate(a) < avg_eng * 0.5]

        # Publish time best slot
        slot_data: Dict[tuple, List[int]] = {}
        DAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        for a in articles:
            if not a.get('published_at'):
                continue
            dt   = datetime.fromisoformat(a['published_at'].replace('Z','+00:00'))
            slot = (dt.weekday(), dt.hour)
            slot_data.setdefault(slot, []).append(a.get('page_views_count',0))
        best_slot = max(slot_data, key=lambda s: sum(slot_data[s])/len(slot_data[s])) if slot_data else None

        # Follower spike articles
        followers = self._followers_cache or []
        week_counts: Dict[str, int] = {}
        for f in followers:
            joined = f.get('created_at') or f.get('joined_at') or ''
            if joined:
                try:
                    wk = datetime.fromisoformat(joined.replace('Z','+00:00')).strftime('%G-W%V')
                    week_counts[wk] = week_counts.get(wk, 0) + 1
                except ValueError:
                    pass

        publish_weeks: Dict[str, List[str]] = {}
        for a in sorted(articles, key=lambda x: x.get('published_at') or ''):
            if a.get('published_at'):
                wk = datetime.fromisoformat(a['published_at'].replace('Z','+00:00')).strftime('%G-W%V')
                publish_weeks.setdefault(wk, []).append(a['title'])

        spike_articles = []
        for w in publish_weeks:
            if w in week_counts and week_counts[w] > 50:
                titles = publish_weeks[w]
                spike_articles.append((week_counts[w], titles[0], titles))
        spike_articles.sort(reverse=True)

        # ── PRINT REPORT ─────────────────────────────────────────────────────
        W = 80
        print(f"\n{'═'*W}")
        print(f"  🧠 GNOMEMAN4201 · DEV.TO INTELLIGENCE REPORT")
        print(f"  Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'═'*W}\n")

        print(f"  PORTFOLIO SNAPSHOT")
        print(f"  {'─'*40}")
        print(f"  Articles:        {len(articles)}")
        print(f"  Total views:     {total_views:,}")
        print(f"  Total reactions: {total_reactions}")
        print(f"  Total comments:  {total_comments}")
        print(f"  Avg views:       {avg_views:.0f}")
        print(f"  Avg engagement:  {avg_eng:.2f}%")

        traj_icon = '📈' if trajectory > 10 else '📉' if trajectory < -10 else '➡️'
        traj_label = f"+{trajectory:.0f}%" if trajectory >= 0 else f"{trajectory:.0f}%"
        print(f"  3-month trend:   {traj_icon} {traj_label} views vs prior 3 months")
        print()

        print(f"  CONTENT STRATEGY  (ranked findings)")
        print(f"  {'─'*40}")

        findings = []

        # Finding: investigative content dominates
        inv_tags = {'security','cybersecurity','github','botnet','infosec','redteam'}
        inv_arts = [a for a in articles if any(t in inv_tags for t in a.get('tag_list',[]))]
        if inv_arts:
            inv_avg = sum(a.get('page_views_count',0) for a in inv_arts) / len(inv_arts)
            other_avg = sum(a.get('page_views_count',0) for a in articles if a not in inv_arts)
            other_avg /= max(len(articles) - len(inv_arts), 1)
            if inv_avg > other_avg:
                findings.append((inv_avg/max(other_avg,1),
                    f"Investigative/security content averages {inv_avg:.0f} views vs "
                    f"{other_avg:.0f} for other content ({inv_avg/max(other_avg,1):.1f}× multiplier). "
                    f"This is your primary content type."))

        # Finding: breakout tags
        if breakout_tags:
            t, s = breakout_tags[0]
            findings.append((s['views']/s['count'],
                f"#{t} is your highest-performing repeated tag "
                f"({s['views']/s['count']:.0f} avg views, {s['count']} articles). "
                f"Use it more deliberately."))

        # Finding: underused high-performers
        if underused_high:
            t, s = underused_high[0]
            findings.append((s['views'],
                f"#{t} produced {s['views']:,} views from a single article — "
                f"you've never used it again. Strong signal to revisit."))

        # Finding: best publish slot
        if best_slot:
            day, hour = best_slot
            slot_avg = sum(slot_data[best_slot]) / len(slot_data[best_slot])
            findings.append((slot_avg,
                f"Best publish slot: {DAYS[day]} {hour:02d}:00 UTC "
                f"({slot_avg:.0f} avg views, {len(slot_data[best_slot])} data point(s)). "
                f"Your current publish pattern is scattered."))

        # Finding: underperformers
        if under:
            formats = []
            for a in under:
                title = a['title']
                if '?' in title:       formats.append('discussion prompts')
                elif len(title) < 40:  formats.append('short-form fragments')
            formats = list(set(formats))
            findings.append((0,
                f"{len(under)} articles underperform significantly (<50% avg views + engagement). "
                + (f"Common format: {', '.join(formats)}. " if formats else '')
                + "Your audience wants full technical arguments, not fragments."))

        # Finding: follower spike pattern
        if spike_articles:
            findings.append((spike_articles[0][0],
                f"Your top follower-driving article generated +{spike_articles[0][0]:,} followers: "
                f'"{spike_articles[0][1][:55]}". '
                f"Concrete investigative findings with named evidence are your growth engine."))

        findings.sort(key=lambda x: x[0], reverse=True)
        for i, (_, text) in enumerate(findings, 1):
            # Word-wrap at W-6
            words = text.split()
            line, lines_out = '', []
            for w in words:
                if len(line) + len(w) + 1 > W - 8:
                    lines_out.append(line)
                    line = w
                else:
                    line = (line + ' ' + w).strip()
            if line:
                lines_out.append(line)
            print(f"  {i}. {lines_out[0]}")
            for l in lines_out[1:]:
                print(f"     {l}")
            print()

        print(f"  TOP CONTENT BY ENGAGEMENT")
        print(f"  {'─'*40}")
        for a in top_eng:
            print(f"  {self.calculate_engagement_rate(a):>5.2f}%  {a['title'][:65]}")
        print()

        print(f"  TOP CONTENT BY VIEWS")
        print(f"  {'─'*40}")
        for a in top_views:
            print(f"  {a.get('page_views_count',0):>6}  {a['title'][:65]}")
        print()

        print(f"  AUDIENCE SIGNAL")
        print(f"  {'─'*40}")
        if followers:
            print(f"  {len(followers):,} followers tracked")
            if spike_articles:
                print(f"  Top 3 follower-driving articles:")
                for count, title, _ in spike_articles[:3]:
                    print(f"    +{count:<6} {title[:60]}")
        else:
            print(f"  Run --follower-correlation first to populate audience data")
        print()

        print(f"  RECOMMENDED NEXT ACTIONS")
        print(f"  {'─'*40}")
        actions = []
        if best_slot:
            day, hour = best_slot
            actions.append(f"Publish next article on {DAYS[day]} at {hour:02d}:00 UTC")
        if breakout_tags:
            actions.append(f"Tag next article with #{breakout_tags[0][0]} (your highest-performing repeat tag)")
        if underused_high:
            actions.append(f"Write a follow-up using #{underused_high[0][0]} (1 article, {underused_high[0][1]['views']:,} views — untapped)")
        if under:
            actions.append(f"Archive or rewrite {len(under)} underperforming articles — they dilute your portfolio avg")
        actions.append("Continue investigative format — it's your strongest content type by all metrics")
        for i, a in enumerate(actions, 1):
            print(f"  {i}. {a}")

        print(f"\n{'═'*W}\n")

    def fetch_articles_full(self) -> List[Dict]:
        """
        Fetch full article bodies via /articles/me/all (already done in fetch_articles).
        Also fetches the public view (/articles?username=) to get flare_tag.
        Merges flare_tag into self.articles in-place. Returns merged list.
        """
        if not self.articles:
            return []
        owner = self._get_own_username() or 'gnomeman4201'
        print(f"🔄 Fetching public article view (flare tags)...")
        try:
            public = []
            page = 1
            while True:
                r = requests.get(
                    f"{self.base_url}/articles",
                    headers=self.headers,
                    params={'username': owner, 'state': 'all',
                            'per_page': 100, 'page': page},
                    timeout=10
                )
                if r.status_code != 200:
                    break
                batch = r.json()
                if not batch:
                    break
                public.extend(batch)
                if len(batch) < 100:
                    break
                page += 1
            slug_to_flare = {a.get('slug'): a.get('flare_tag') for a in public}
            for article in self.articles:
                ft = slug_to_flare.get(article.get('slug'))
                article['flare_tag'] = ft
            print(f"✅ Merged flare tags for {len(self.articles)} articles\n")
        except Exception as e:
            print(f"⚠️  Could not fetch public view: {e}\n")
        return self.articles

    def content_analysis(self):
        """
        Deep analysis of article body_markdown across all articles.
        Covers: word counts, sentence length, reading grade estimate,
        vocabulary richness, most-mentioned tools/repos/concepts,
        internal vs external link density, title length vs views correlation,
        and edit history (edited_at vs published_at gap).
        """
        import re
        from html.parser import HTMLParser

        # We need body_markdown — fetch individually if not present
        articles_with_body = [a for a in self.articles if a.get('body_markdown')]
        if not articles_with_body:
            print("🔄 Fetching article bodies (body_markdown)...")
            enriched = []
            for article in self.articles:
                aid = article.get('id')
                if not aid:
                    continue
                try:
                    r = requests.get(
                        f"{self.base_url}/articles/{aid}",
                        headers=self.headers, timeout=10
                    )
                    if r.status_code == 200:
                        data = r.json()
                        article['body_markdown'] = data.get('body_markdown', '')
                        article['body_html']     = data.get('body_html', '')
                        enriched.append(article)
                except Exception:
                    pass
            print(f"✅ Fetched bodies for {len(enriched)} articles\n")
            articles_with_body = enriched

        if not articles_with_body:
            print("❌ No article bodies available")
            return

        # ── per-article stats ─────────────────────────────────────────────────
        # Tech signals — tuples of (display_name, regex_pattern)
        # Short/ambiguous tokens use strict word-boundary patterns to avoid
        # false positives ('go' matching 'going', 'git' matching 'digital', etc.)
        TECH_SIGNALS = [
            ('python',       r'\bpython\b'),
            ('javascript',   r'\bjavascript\b'),
            ('typescript',   r'\btypescript\b'),
            ('bash',         r'\bbash\b'),
            ('shell',        r'\bshell\b'),
            ('sql',          r'\bsql\b'),
            ('rust',         r'\brust\b'),
            ('go/golang',    r'\bgolang\b|\bgo\s+(?:to|build|run|install|get|mod|test)\b'),
            ('docker',       r'\bdocker\b'),
            ('kubernetes',   r'\bkubernetes\b|\bk8s\b'),
            ('linux',        r'\blinux\b'),
            ('git',          r'\bgit\s+(?:commit|push|pull|clone|add|diff|log|branch|checkout|merge|rebase|stash|tag)\b|\bgit\b(?=\s+[a-z]+\b)'),
            ('github',       r'\bgithub\.com\b|\bgithub\b'),
            ('api',          r'\bapi\b(?!\w)'),
            ('json',         r'\bjson\b'),
            ('yaml',         r'\byaml\b'),
            ('shenron',      r'\bshenron\b'),
            ('lanimorph',    r'\blanimorph\b'),
            ('chain',        r'\bchain\b(?!\s+(?:of|reaction|store))'),
            ('sigma',        r'\bsigma\b(?!\s+(?:male|female))'),
            ('suricata',     r'\bsuricata\b'),
            ('splunk',       r'\bsplunk\b'),
            ('elastic',      r'\belastic(?:search)?\b'),
            ('nmap',         r'\bnmap\b'),
            ('burp',         r'\bburp(?:\s+suite)?\b'),
            ('metasploit',   r'\bmetasploit\b'),
            ('mitre',        r'\bmitre\b'),
            ('att&ck',       r'\batt&ck\b|\battack\s+framework\b'),
            ('cve',          r'\bcve-?\d+\b|\bcve\b'),
            ('exploit',      r'\bexploit(?:ed|ing|ation)?\b'),
            ('llm',          r'\bllm\b|\blarge\s+language\s+model\b'),
            ('openai',       r'\bopenai\b'),
            ('anthropic',    r'\banthropic\b'),
            ('claude',       r'\bclaude\b'),
            ('gpt',          r'\bgpt-?\d*\b'),
            ('langchain',    r'\blangchain\b'),
            ('ollama',       r'\bollama\b'),
            ('flask',        r'\bflask\b'),
            ('fastapi',      r'\bfastapi\b'),
            ('django',       r'\bdjango\b'),
            ('react',        r'\breact(?:\.js)?\b'),
            ('node',         r'\bnode(?:\.js)?\b'),
            ('postgres',     r'\bpostgres(?:ql)?\b'),
            ('sqlite',       r'\bsqlite\b'),
            ('regex',        r'\bregex\b|\bregexp\b'),
            ('xpath',        r'\bxpath\b'),
            ('graphql',      r'\bgraphql\b'),
            ('grpc',         r'\bgrpc\b'),
            ('oauth',        r'\boauth\b'),
            ('jwt',          r'\bjwt\b'),
            ('hmac',         r'\bhmac\b'),
            ('sha',          r'\bsha-?(?:1|2|256|512)\b'),
        ]
        _sig_compiled = [(name, re.compile(pat, re.IGNORECASE)) for name, pat in TECH_SIGNALS]

        URL_RE    = re.compile(r'https?://\S+')
        SENT_RE   = re.compile(r'[.!?]+')
        WORD_RE   = re.compile(r'\b[a-zA-Z]{3,}\b')
        MD_STRIP  = re.compile(r'```.*?```|`[^`]+`|!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)|#+\s|[*_~>]', re.DOTALL)

        stats = []
        all_words: List[str] = []
        tool_mentions: Dict[str, int] = {}
        int_links_total, ext_links_total = 0, 0

        for article in articles_with_body:
            body = article.get('body_markdown', '')
            clean = MD_STRIP.sub(' ', body)
            words = WORD_RE.findall(clean.lower())
            sentences = [s.strip() for s in SENT_RE.split(clean) if s.strip()]
            n_words = len(words)
            n_sents = max(len(sentences), 1)
            avg_sent = n_words / n_sents
            unique_words = len(set(words))
            vocab_richness = unique_words / max(n_words, 1)

            urls = URL_RE.findall(body)
            int_links = sum(1 for u in urls if 'dev.to' in u or 'github.com/GnomeMan' in u.lower())
            ext_links = len(urls) - int_links

            # Edit gap
            pub  = article.get('published_at', '')
            edit = article.get('edited_at', '')
            edit_gap_days = None
            if pub and edit:
                try:
                    pd = datetime.fromisoformat(pub.replace('Z','+00:00'))
                    ed = datetime.fromisoformat(edit.replace('Z','+00:00'))
                    edit_gap_days = max(0, (ed - pd).days)
                except Exception:
                    pass

            # Tool mentions — regex-based, avoids false positives
            for name, pat in _sig_compiled:
                count = len(pat.findall(body))
                if count:
                    tool_mentions[name] = tool_mentions.get(name, 0) + count

            all_words.extend(words)
            stats.append({
                'title':         article['title'],
                'views':         article.get('page_views_count', 0),
                'eng':           self.calculate_engagement_rate(article),
                'words':         n_words,
                'sentences':     n_sents,
                'avg_sent_len':  avg_sent,
                'vocab_richness':vocab_richness,
                'unique_words':  unique_words,
                'int_links':     int_links,
                'ext_links':     ext_links,
                'title_len':     len(article.get('title', '')),
                'edit_gap_days': edit_gap_days,
                'flare_tag':     article.get('flare_tag'),
            })

        n = len(stats)
        avg_words    = sum(s['words'] for s in stats) / n
        avg_vocab    = sum(s['vocab_richness'] for s in stats) / n
        avg_sent_len = sum(s['avg_sent_len'] for s in stats) / n
        avg_ext      = sum(s['ext_links'] for s in stats) / n

        # Correlation: title length vs views
        tl_corr_data = [(s['title_len'], s['views']) for s in stats if s['views'] > 0]
        if len(tl_corr_data) > 3:
            tl_mean = sum(x for x,_ in tl_corr_data) / len(tl_corr_data)
            vw_mean = sum(y for _,y in tl_corr_data) / len(tl_corr_data)
            num   = sum((x-tl_mean)*(y-vw_mean) for x,y in tl_corr_data)
            denom = (sum((x-tl_mean)**2 for x,_ in tl_corr_data) *
                     sum((y-vw_mean)**2 for _,y in tl_corr_data)) ** 0.5
            tl_corr = num / denom if denom else 0
        else:
            tl_corr = 0

        # Word count vs views
        wv_data = [(s['words'], s['views']) for s in stats if s['views'] > 0]
        if len(wv_data) > 3:
            wm = sum(x for x,_ in wv_data) / len(wv_data)
            vm = sum(y for _,y in wv_data) / len(wv_data)
            num = sum((x-wm)*(y-vm) for x,y in wv_data)
            den = (sum((x-wm)**2 for x,_ in wv_data) * sum((y-vm)**2 for _,y in wv_data)) ** 0.5
            wv_corr = num / den if den else 0
        else:
            wv_corr = 0

        # Top/bottom by word count
        by_words = sorted(stats, key=lambda s: s['words'], reverse=True)

        # Flare tag distribution
        flare_dist: Dict[str, int] = {}
        for s in stats:
            ft = s['flare_tag']
            name = ft['name'] if ft and isinstance(ft, dict) else 'none'
            flare_dist[name] = flare_dist.get(name, 0) + 1

        # Edited articles
        edited = [s for s in stats if s['edit_gap_days'] is not None and s['edit_gap_days'] > 0]

        print(f"\n📝 CONTENT ANALYSIS")
        print(f"   Based on {n} articles with full body text")
        print("="*90)

        print(f"\n  CORPUS OVERVIEW")
        print(f"  {'─'*50}")
        total_words = sum(s['words'] for s in stats)
        print(f"  Total words written:     {total_words:,}")
        print(f"  Avg words/article:       {avg_words:.0f}")
        print(f"  Avg sentence length:     {avg_sent_len:.1f} words")
        print(f"  Avg vocab richness:      {avg_vocab:.2f}  (unique/total words, higher=more varied)")
        print(f"  Avg external links:      {avg_ext:.1f}/article")

        print(f"\n  CORRELATIONS")
        print(f"  {'─'*50}")
        def corr_label(r):
            if abs(r) < 0.2:  return "negligible"
            if abs(r) < 0.4:  return "weak"
            if abs(r) < 0.6:  return "moderate"
            if abs(r) < 0.8:  return "strong"
            return "very strong"
        tl_dir = "positive" if tl_corr > 0 else "negative"
        wv_dir = "positive" if wv_corr > 0 else "negative"
        print(f"  Title length vs views:   r={tl_corr:+.3f}  ({corr_label(tl_corr)} {tl_dir})")
        print(f"  Word count vs views:     r={wv_corr:+.3f}  ({corr_label(wv_corr)} {wv_dir})")

        print(f"\n  WORD COUNT DISTRIBUTION")
        print(f"  {'─'*50}")
        for s in by_words[:5]:
            bar = '█' * min(40, int(s['words'] / max(by_words[0]['words'], 1) * 40))
            print(f"  {s['words']:>5}w  {bar:<40}  {s['title'][:40]}")
        print(f"  ...")
        for s in by_words[-3:]:
            bar = '█' * max(1, int(s['words'] / max(by_words[0]['words'], 1) * 40))
            print(f"  {s['words']:>5}w  {bar:<40}  {s['title'][:40]}")

        print(f"\n  TOP TECH/TOOL MENTIONS (across all articles)")
        print(f"  {'─'*50}")
        top_tools = sorted(tool_mentions.items(), key=lambda x: -x[1])[:20]
        max_count = top_tools[0][1] if top_tools else 1
        for tool, count in top_tools:
            bar = '█' * int(count / max_count * 30)
            print(f"  {tool:<20} {bar:<30} {count}×")

        print(f"\n  FLARE TAG DISTRIBUTION")
        print(f"  {'─'*50}")
        for name, count in sorted(flare_dist.items(), key=lambda x: -x[1]):
            print(f"  #{name:<20} {count} article{'s' if count != 1 else ''}")

        print(f"\n  EDIT HISTORY")
        print(f"  {'─'*50}")
        print(f"  Articles edited after publish: {len(edited)}/{n}")
        if edited:
            for s in sorted(edited, key=lambda x: x['edit_gap_days'], reverse=True)[:5]:
                print(f"  +{s['edit_gap_days']:>3}d  {s['title'][:65]}")

        print(f"\n  LINK DENSITY")
        print(f"  {'─'*50}")
        by_ext = sorted(stats, key=lambda s: s['ext_links'], reverse=True)
        for s in by_ext[:5]:
            print(f"  {s['ext_links']:>3} ext  {s['int_links']:>2} int  {s['title'][:60]}")

        print()

    def commenter_enrichment(self, top_n: int = 15):
        """
        Enrich top commenters with full DEV.to profile data via /api/users/{username}.
        Surfaces: DEV follower count, GitHub handle, Twitter handle, website,
        join date, and whether they're in your follower list.
        """
        comments_by = self.fetch_comments()
        if not comments_by:
            print("❌ No comment data")
            return

        OWNER = self._get_own_username()
        commenter_counts: Dict[str, int] = {}
        commenter_usernames: Dict[str, str] = {}
        for aid, comments in comments_by.items():
            for c in comments:
                u = c['username']
                if not u or u.lower() == OWNER:
                    continue
                commenter_counts[u.lower()] = commenter_counts.get(u.lower(), 0) + 1
                commenter_usernames[u.lower()] = u

        ranked = sorted(commenter_counts.items(), key=lambda x: -x[1])[:top_n]
        follower_set = {f.get('username','').lower() for f in (self._followers_cache or [])}

        print(f"\n🔍 COMMENTER PROFILE ENRICHMENT (top {top_n})")
        print("="*110)
        print(f"  {'Username':<25} {'Cmts':<6} {'Follower':<10} {'DEV joined':<14} {'GitHub':<22} {'Website'}")
        print("  " + "─"*100)

        enriched = []
        for ukey, count in ranked:
            username = commenter_usernames[ukey]
            try:
                r = requests.get(
                    f"{self.base_url}/users/by_username",
                    headers=self.headers,
                    params={'url': username},
                    timeout=8
                )
                if r.status_code == 200:
                    p = r.json()
                else:
                    p = {}
            except Exception:
                p = {}

            is_follower = '✅' if ukey in follower_set else '  '
            joined      = (p.get('joined_at') or '')[:10]
            github      = p.get('github_username') or '—'
            twitter     = p.get('twitter_username') or '—'
            website     = (p.get('website_url') or '—')[:35]
            dev_follows = p.get('followers_count', '?')

            print(f"  @{username:<24} {count:<6} {is_follower:<10} {joined:<14} "
                  f"gh:{github:<20} {website}")

            enriched.append({
                'username': username,
                'comments': count,
                'is_follower': ukey in follower_set,
                'joined_at': joined,
                'github_username': github,
                'twitter_username': twitter,
                'website_url': website,
                'dev_followers': dev_follows,
                'profile': p,
            })

        # Surface notable finds
        with_github = [e for e in enriched if e['github_username'] != '—']
        followers_who_comment = [e for e in enriched if e['is_follower']]
        non_followers = [e for e in enriched if not e['is_follower']]

        print(f"\n  📎 {len(with_github)}/{len(enriched)} top commenters have linked GitHub accounts:")
        for e in with_github:
            print(f"     @{e['username']:<25} → github.com/{e['github_username']}")

        if non_followers:
            print(f"\n  💡 Top commenters who haven't followed ({len(non_followers)}):")
            for e in non_followers[:5]:
                print(f"     @{e['username']:<25} {e['comments']} comments")

        print()

    def reading_list(self):
        """
        Fetch your DEV.to reading list (articles you've saved).
        Analyse: which tags you're consuming, authors you follow,
        topics you read vs topics you write about.
        """
        print("🔄 Fetching your reading list...")
        saved = []
        page  = 1
        while True:
            try:
                r = requests.get(
                    f"{self.base_url}/readinglist",
                    headers=self.headers,
                    params={'per_page': 100, 'page': page},
                    timeout=10
                )
                if r.status_code != 200:
                    break
                batch = r.json()
                if not batch:
                    break
                saved.extend(batch)
                if len(batch) < 100:
                    break
                page += 1
            except Exception as e:
                print(f"❌ Error: {e}")
                break

        if not saved:
            print("❌ Reading list empty or not accessible\n")
            return

        print(f"✅ Loaded {len(saved)} saved articles\n")

        # Each item has 'article' nested
        articles_saved = [item.get('article', item) for item in saved]

        # Tag consumption — handle both list ['a','b'] and string 'a, b' formats
        def parse_tags(val):
            if not val:
                return []
            if isinstance(val, list):
                return [t.strip() for t in val if t.strip()]
            if isinstance(val, str):
                return [t.strip() for t in val.split(',') if t.strip()]
            return []

        tag_read: Dict[str, int] = {}
        for a in articles_saved:
            for t in parse_tags(a.get('tag_list') or a.get('tags')):
                tag_read[t] = tag_read.get(t, 0) + 1

        # Author consumption
        author_read: Dict[str, int] = {}
        for a in articles_saved:
            u = (a.get('user') or {}).get('username', '')
            if u:
                author_read[u] = author_read.get(u, 0) + 1

        # Tags you write vs tags you read
        write_tags = set()
        for a in self.articles:
            write_tags.update(a.get('tag_list', []))
        read_only_tags  = [t for t in tag_read if t not in write_tags]
        write_only_tags = [t for t in write_tags if t not in tag_read]

        print(f"  📚 READING LIST ANALYSIS  ({len(saved)} saved articles)")
        print("="*80)

        print(f"\n  Top tags you're consuming:")
        top_read = sorted(tag_read.items(), key=lambda x: -x[1])[:15]
        max_r = top_read[0][1] if top_read else 1
        for tag, count in top_read:
            bar = '█' * int(count / max_r * 30)
            in_writing = ' ✍️' if tag in write_tags else ''
            print(f"  #{tag:<22} {bar:<30} {count}×{in_writing}")

        print(f"\n  Top authors you're reading:")
        top_authors = sorted(author_read.items(), key=lambda x: -x[1])[:10]
        for author, count in top_authors:
            print(f"  @{author:<25} {count} article{'s' if count!=1 else ''} saved")

        print(f"\n  Tags you READ but never WRITE about ({len(read_only_tags)} total):")
        print(f"  " + ', '.join(f'#{t}' for t in sorted(read_only_tags, key=lambda t: -tag_read[t])[:12]))

        print(f"\n  Tags you WRITE about but never READ ({len(write_only_tags)} total):")
        print(f"  " + ', '.join(f'#{t}' for t in sorted(write_only_tags)[:12]))

        print()

    def followed_tags_analysis(self):
        """
        Fetch tags you follow on DEV.to and cross-reference against
        your writing tags and top tags by audience size.
        """
        print("🔄 Fetching followed tags...")
        followed_map = {}
        # Try multiple endpoint paths — DEV.to's /followed_tags is documented
        # but intermittently disabled on the production instance
        paths = ['/followed_tags', '/tags/followed', '/follows/tags']
        for path in paths:
            try:
                headers_v1 = {**self.headers,
                              'Accept': 'application/vnd.forem.api-v1+json'}
                r = requests.get(
                    f"{self.base_url}{path}",
                    headers=headers_v1, timeout=8
                )
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list) and data:
                        followed_map = {t['name']: t.get('points', 0)
                                        for t in data if t.get('name')}
                        print(f"✅ Following {len(followed_map)} tags (via {path})\n")
                        break
            except Exception:
                continue

        if not followed_map:
            # Fallback: infer from reading list tags (what you actually consume)
            print("⚠️  /followed_tags endpoint unavailable on DEV.to production.")
            print("    Falling back to reading list tag inference...\n")
            saved = []
            try:
                page = 1
                while True:
                    r = requests.get(f"{self.base_url}/readinglist",
                                     headers=self.headers,
                                     params={{'per_page':100,'page':page}}, timeout=10)
                    if r.status_code != 200: break
                    batch = r.json()
                    if not batch: break
                    saved.extend(batch); page += 1
                    if len(batch) < 100: break
            except Exception:
                pass

            def parse_tags(val):
                if not val: return []
                if isinstance(val, list): return [t.strip() for t in val if t.strip()]
                if isinstance(val, str):  return [t.strip() for t in val.split(',') if t.strip()]
                return []

            tag_counts: Dict[str, int] = {{}}
            for item in saved:
                a = item.get('article', item)
                for t in parse_tags(a.get('tag_list') or a.get('tags')):
                    tag_counts[t] = tag_counts.get(t, 0) + 1

            if not tag_counts:
                print("❌ No tag data available from reading list either\n")
                return

            # Treat reading list frequency as proxy for follow interest
            followed_map = tag_counts
            print(f"✅ Inferred {len(followed_map)} tags from reading list ({len(saved)} saved articles)\n")

        # Your writing tags
        write_tags: Dict[str, int] = {}
        for a in self.articles:
            for t in a.get('tag_list', []):
                write_tags[t] = write_tags.get(t, 0) + a.get('page_views_count', 0)

        follow_and_write = [t for t in followed_map if t in write_tags]
        follow_not_write = [t for t in followed_map if t not in write_tags]
        write_not_follow = [t for t in write_tags if t not in followed_map]

        print(f"  🏷️  FOLLOWED TAGS ANALYSIS")
        print("="*80)

        print(f"\n  Tags you follow AND write about ({len(follow_and_write)}) — aligned:")
        for t in sorted(follow_and_write, key=lambda t: -write_tags[t])[:10]:
            pts = followed_map[t]
            views = write_tags[t]
            print(f"  #{t:<25} points:{pts:<6} views from your articles:{views:,}")

        print(f"\n  Tags you follow but NEVER write about ({len(follow_not_write)}) — potential gaps:")
        for t in sorted(follow_not_write, key=lambda t: -followed_map[t])[:10]:
            print(f"  #{t:<25} points:{followed_map[t]}")

        print(f"\n  Tags you write about but DON'T follow ({len(write_not_follow)}) — misaligned:")
        for t in sorted(write_not_follow, key=lambda t: -write_tags[t])[:10]:
            views = write_tags[t]
            print(f"  #{t:<25} {views:,} views from your articles — not in your feed")

        print()

    def competitive_tags(self, top_n: int = 10):
        """
        For your top writing tags, fetch the current top-performing articles
        in that tag on DEV.to. Shows what's working in your competitive space
        right now — view counts, reaction counts, publication recency.
        """
        # Get your top tags by total views
        tag_views: Dict[str, int] = {}
        for a in self.articles:
            for t in a.get('tag_list', []):
                tag_views[t] = tag_views.get(t, 0) + a.get('page_views_count', 0)

        top_tags = sorted(tag_views.items(), key=lambda x: -x[1])[:6]

        print(f"\n🏆 COMPETITIVE TAG ANALYSIS")
        print(f"   Top articles in your primary tags right now on DEV.to")
        print("="*100)

        for tag, your_views in top_tags:
            try:
                r = requests.get(
                    f"{self.base_url}/articles",
                    headers=self.headers,
                    params={'tag': tag, 'top': 7, 'per_page': 5},
                    timeout=10
                )
                if r.status_code != 200:
                    continue
                top_arts = r.json()
            except Exception:
                continue

            own_username = self._get_own_username()
            print(f"\n  #{tag}  (your total: {your_views:,} views)")
            print(f"  {'─'*80}")
            for a in top_arts[:5]:
                author = (a.get('user') or {}).get('username', '?')
                is_you = ' ← YOU' if author.lower() == own_username else ''
                reactions = a.get('public_reactions_count', 0)
                pub = (a.get('published_at') or '')[:10]
                title = (a.get('title') or '')[:55]
                print(f"  {reactions:>5}❤️  {pub}  @{author:<20} {title}{is_you}")

        print()


    def tag_fix_suggestions(self):
        """
        For each article, scan body_markdown for tech signals and
        high-value tags you follow, then diff against current tags.
        Output: per-article list of suggested tags to add, with the
        DEV.to edit URL so you can action each one immediately.
        Also outputs a global summary of the highest-leverage additions.
        """
        import re

        # ── fetch bodies if needed ────────────────────────────────────────────
        articles_with_body = [a for a in self.articles if a.get('body_markdown')]
        if not articles_with_body:
            print("🔄 Fetching article bodies...")
            for article in self.articles:
                aid = article.get('id')
                if not aid:
                    continue
                try:
                    r = requests.get(f"{self.base_url}/articles/{aid}",
                                     headers=self.headers, timeout=10)
                    if r.status_code == 200:
                        data = r.json()
                        article['body_markdown'] = data.get('body_markdown', '')
                except Exception:
                    pass
            articles_with_body = [a for a in self.articles if a.get('body_markdown')]
            print(f"✅ Bodies loaded for {len(articles_with_body)} articles\n")

        # ── tag signal map: tag → (regex, min_hits) ──────────────────────────
        # Each entry: if the regex matches >= min_hits times in the body,
        # the tag is a strong candidate. Ordered by priority.
        TAG_SIGNALS: List[tuple] = [
            # High-value misaligned tags from your profile
            ('cybersecurity',    re.compile(r'\b(?:attack|threat|vuln|malware|phish|breach|incident|adversar|cve|exploit|pentest|redteam|blueteam|soc|siem|ioc|ttps?)\b', re.I), 3),
            ('llm',              re.compile(r'\b(?:llm|large\s+language|language\s+model|gpt|claude|gemini|prompt\s+inject|hallucin|fine.?tun|token|embedding|inference|rag|chain.of.thought)\b', re.I), 2),
            ('github',           re.compile(r'\bgithub\.com\b|\bgithub\s+(?:api|actions|workflow|repo|issue|pr|pull.request|commit|fork|star|follower)\b', re.I), 2),
            ('promptengineering',re.compile(r'\bprompt\s+(?:engineer|inject|design|optim|templ|chain|format|craft|hack)\b|\bsystem\s+prompt\b|\bfew.shot\b|\bzero.shot\b', re.I), 2),
            ('git',              re.compile(r'\bgit\s+(?:commit|push|pull|clone|add|diff|log|branch|checkout|merge|rebase|stash|bisect|tag|blame|cherry)\b', re.I), 2),
            ('bash',             re.compile(r'\b(?:bash|#!/bin/bash|#!/bin/sh|shell\s+script|#!/usr/bin/env\s+bash|grep|awk|sed|curl|wget|chmod|cron|systemd|alias|bashrc|zshrc)\b', re.I), 3),
            ('sql',              re.compile(r'\b(?:select\s+\*?|insert\s+into|update\s+\w+\s+set|delete\s+from|join\s+\w|where\s+\w|sqlite|postgres|mysql|sql\s+inject)\b', re.I), 2),
            ('graphql',          re.compile(r'\bgraphql\b|\bgql\b|\bquery\s*\{|\bmutation\s*\{|\bsubscription\s*\{', re.I), 2),
            ('typescript',       re.compile(r'\btypescript\b|\.ts\b|\binterface\s+\w+\s*\{|\btype\s+\w+\s*=', re.I), 2),
            ('docker',           re.compile(r'\bdocker\b|\bdockerfile\b|\bcontainer(?:ize|ized|ization)?\b|\bdocker-compose\b', re.I), 2),
            ('api',              re.compile(r'\brest\s+api\b|\bapi\s+(?:endpoint|key|token|call|request|response|rate.limit)\b|\bopenapi\b|\bswagger\b', re.I), 3),
            ('python',           re.compile(r'\bpython\b|\bpip\s+install\b|\.py\b|\bvenv\b|\brequirements\.txt\b', re.I), 3),
            ('linux',            re.compile(r'\blinux\b|\bubuntu\b|\bdebian\b|\barch\b|\bkali\b|\bsystemd\b|\b/etc/\b|\b/usr/\b', re.I), 2),
            ('opensource',       re.compile(r'\bopen.?source\b|\bgithub\.com/\w+/\w+\b|\bmit\s+licen\b|\bapache\s+licen\b|\bcontribut\b', re.I), 2),
            ('devops',           re.compile(r'\bci/cd\b|\bpipeline\b|\bgithub\s+actions\b|\bjenkins\b|\bterraform\b|\bansible\b|\bkubernetes\b|\bdeployment\b', re.I), 2),
            ('testing',          re.compile(r'\bunit\s+test\b|\bpytest\b|\bjest\b|\bmock\b|\bfixture\b|\btest\s+suite\b|\bcoverage\b|\btdd\b', re.I), 2),
            ('webdev',           re.compile(r'\bhtml\b|\bcss\b|\bjavascript\b|\bfrontend\b|\bresponsive\b|\bdom\b|\bwebpack\b|\bnext\.js\b', re.I), 3),
            ('machinelearning',  re.compile(r'\bmachine\s+learning\b|\bml\s+model\b|\btraining\s+data\b|\bneural\s+net\b|\bclassif\b|\bregress\b|\bprediction\b', re.I), 2),
            ('discuss',          re.compile(r'^#{1,2}\s+.*\?|\bwhat\s+(?:do|did|would|should)\s+you\b|\blet\s+me\s+know\b|\bshare\s+your\b', re.I | re.MULTILINE), 3),
        ]

        # Max 4 tags per article on DEV.to
        MAX_TAGS = 4

        print(f"\n🏷️  TAG FIX SUGGESTIONS")
        print(f"   Scanning {len(articles_with_body)} articles for missing high-value tags")
        print("="*100)

        global_additions: Dict[str, int] = {}  # tag → how many articles it should be added to
        all_suggestions = []

        for article in sorted(articles_with_body,
                              key=lambda a: a.get('page_views_count', 0), reverse=True):
            body   = article.get('body_markdown', '')
            title  = article.get('title', '')
            url    = article.get('url', '')
            slug   = article.get('slug', '')
            views  = article.get('page_views_count', 0)
            current_tags = set(article.get('tag_list') or [])
            slots_free = MAX_TAGS - len(current_tags)

            # Find which signal tags are present in body
            matched_tags = []
            for tag, pattern, min_hits in TAG_SIGNALS:
                if tag in current_tags:
                    continue  # already tagged
                hits = len(pattern.findall(body + ' ' + title))
                if hits >= min_hits:
                    matched_tags.append((tag, hits))

            # Sort by hit count descending, take up to free slots
            matched_tags.sort(key=lambda x: -x[1])
            suggestions = matched_tags[:max(slots_free, 3)]  # show up to 3 even if slots full

            if not suggestions:
                continue

            # Build edit URL
            owner   = self._get_own_username() or 'gnomeman4201'
            edit_url = f"https://dev.to/{owner}/{slug}/edit" if slug else url

            all_suggestions.append({
                'title':        title,
                'views':        views,
                'current_tags': sorted(current_tags),
                'suggestions':  suggestions,
                'slots_free':   slots_free,
                'edit_url':     edit_url,
            })

            for tag, hits in suggestions:
                global_additions[tag] = global_additions.get(tag, 0) + 1

        if not all_suggestions:
            print("\n  ✅ No obvious tag gaps detected across your articles.\n")
            return

        # ── per-article output ────────────────────────────────────────────────
        for s in all_suggestions:
            can_add  = [t for t, _ in s['suggestions'][:s['slots_free']]]
            overflow = [t for t, _ in s['suggestions'][s['slots_free']:]]

            print(f"\n  📄 {s['title'][:70]}")
            print(f"     Views: {s['views']:,}  |  Current tags: {', '.join('#'+t for t in s['current_tags']) or '(none)'}  |  Free slots: {s['slots_free']}")

            if can_add:
                print(f"     ➕ ADD:    {', '.join('#'+t for t in can_add)}")
            if overflow:
                print(f"     ⚠️  FULL — consider swapping: {', '.join('#'+t for t in overflow)}")
            print(f"     🔗 {s['edit_url']}")

        # ── global summary ────────────────────────────────────────────────────
        print(f"\n{'─'*100}")
        print(f"  📊 GLOBAL TAG OPPORTUNITY SUMMARY")
        print(f"     (tags you should add across multiple articles)")
        print(f"{'─'*100}")
        for tag, count in sorted(global_additions.items(), key=lambda x: -x[1]):
            bar = '█' * min(count * 4, 40)
            print(f"  #{tag:<22} {bar:<40} applies to {count} article{'s' if count != 1 else ''}")

        print(f"\n  💡 QUICK WINS  (add these tags first — highest views × most applicable)")
        # Score = sum of views of articles where this tag is missing
        tag_view_score: Dict[str, int] = {}
        for s in all_suggestions:
            for tag, _ in s['suggestions']:
                tag_view_score[tag] = tag_view_score.get(tag, 0) + s['views']
        top_wins = sorted(tag_view_score.items(), key=lambda x: -x[1])[:5]
        for tag, score in top_wins:
            n = global_additions[tag]
            print(f"  #{tag:<22} → {score:,} combined views across {n} article{'s' if n!=1 else ''} that need it")

        print()

    # ─── EXPORT ──────────────────────────────────────────────────────────────

    def export_json(self, filename: str, days: int = None):
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
        articles = self.filter_by_date(days)
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Title','URL','Published','Views','Reactions',
                             'Comments','Engagement %','Reading Time','Tags','Canonical URL'])
            for article in articles:
                writer.writerow([
                    article['title'],
                    article['url'],
                    article['published_at'][:10] if article['published_at'] else "Unpublished",
                    article.get('page_views_count', 0),
                    article.get('public_reactions_count', 0),
                    article.get('comments_count', 0),
                    f"{self.calculate_engagement_rate(article):.2f}",
                    article.get('reading_time_minutes', 0),
                    ', '.join(article.get('tag_list', [])),
                    article.get('canonical_url', '')
                ])
        print(f"✅ Data exported to {filename}")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Dev.to Analytics Pro — advanced analytics for your articles',
        epilog='''
Examples:
  python dev.py --api-key KEY --overview
  python dev.py --api-key KEY --top 20 --sort engagement
  python dev.py --api-key KEY --tags --days 90
  python dev.py --api-key KEY --series
  python dev.py --api-key KEY --follower-correlation
  python dev.py --api-key KEY --publish-heatmap
  python dev.py --api-key KEY --cross-platform
  python dev.py --api-key KEY --full-report
  python dev.py --api-key KEY --tag-fix
  python dev.py --api-key KEY --export-csv analytics.csv
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--api-key', required=True, help='Your Dev.to API key')

    # Existing flags
    parser.add_argument('--overview',        action='store_true', help='Show overview statistics')
    parser.add_argument('--top',             type=int, metavar='N', help='Show top N articles')
    parser.add_argument('--sort',            choices=['views','reactions','comments','engagement'],
                                             default='views')
    parser.add_argument('--tags',            action='store_true', help='Tag performance analysis')
    parser.add_argument('--reading-time',    action='store_true', help='Reading time analysis')
    parser.add_argument('--growth',          action='store_true', help='Month-over-month growth')
    parser.add_argument('--underperformers', action='store_true', help='Underperformer detection')
    parser.add_argument('--days',            type=int, help='Filter by last N days')
    parser.add_argument('--export-json',     metavar='FILE', help='Export to JSON')
    parser.add_argument('--export-csv',      metavar='FILE', help='Export to CSV')
    parser.add_argument('--full-report',     action='store_true', help='Full analytics report')

    # New flags
    parser.add_argument('--series',               action='store_true',
                        help='Series performance — detect and analyse multi-part articles')
    parser.add_argument('--follower-correlation',  action='store_true',
                        help='Correlate follower growth with publish events')
    parser.add_argument('--publish-heatmap',      action='store_true',
                        help='Day × hour heatmap of average views per publish time')
    parser.add_argument('--cross-platform',       action='store_true',
                        help='Cross-platform reach estimation via canonical URL analysis')
    parser.add_argument('--commenters',           action='store_true',
                        help='Rank commenters by frequency across all articles')
    parser.add_argument('--loyal-readers',        action='store_true',
                        help='Cross-reference commenters with followers to find your core audience')
    parser.add_argument('--insights',             action='store_true',
                        help='Synthesised intelligence report — ranked findings and recommended actions')
    parser.add_argument('--content-analysis',     action='store_true',
                        help='Deep body_markdown analysis — word counts, vocab, tool mentions, correlations')
    parser.add_argument('--commenter-enrichment', action='store_true',
                        help='Enrich top commenters with full DEV.to profile data (GitHub, Twitter, etc.)')
    parser.add_argument('--reading-list',         action='store_true',
                        help='Analyse your DEV.to reading list vs what you write about')
    parser.add_argument('--followed-tags',        action='store_true',
                        help='Compare tags you follow vs tags you write about')
    parser.add_argument('--competitive-tags',     action='store_true',
                        help='Top articles in your primary tags right now on DEV.to')
    parser.add_argument('--flare-tags',           action='store_true',
                        help='Fetch flare tag data from public article view and merge')
    parser.add_argument('--tag-fix',              action='store_true',
                        help='Scan article bodies for missing high-value tags — outputs edit URLs')
    parser.add_argument('--enrich-top', type=int, metavar='N', default=15,
                        help='Number of top commenters to enrich (default: 15)')

    args = parser.parse_args()

    analytics = DevToAnalytics(args.api_key)
    analytics.fetch_articles()

    if args.full_report:
        analytics.overview(args.days)
        analytics.top_articles(10, args.sort, args.days)
        analytics.tag_analysis(args.days)
        analytics.reading_time_analysis(args.days)
        analytics.growth_trends()
        analytics.underperformers(args.days or 30)
        analytics.series_analysis()
        analytics.publish_time_heatmap()
        analytics.cross_platform_reach()
        analytics.fetch_followers()
        analytics.follower_correlation()
        analytics.commenters()
        analytics.commenter_enrichment()
        analytics.loyal_readers()
        analytics.content_analysis()
        analytics.reading_list()
        analytics.followed_tags_analysis()
        analytics.competitive_tags()
        analytics.fetch_articles_full()
        analytics.tag_fix_suggestions()
        analytics.insights()
    else:
        if args.overview:          analytics.overview(args.days)
        if args.top:               analytics.top_articles(args.top, args.sort, args.days)
        if args.tags:              analytics.tag_analysis(args.days)
        if args.reading_time:      analytics.reading_time_analysis(args.days)
        if args.growth:            analytics.growth_trends()
        if args.underperformers:   analytics.underperformers(args.days or 30)
        if args.series:            analytics.series_analysis()
        if args.publish_heatmap:   analytics.publish_time_heatmap()
        if args.cross_platform:    analytics.cross_platform_reach()
        if args.follower_correlation:
            analytics.fetch_followers()
            analytics.follower_correlation()
        if args.commenters:        analytics.commenters()
        if args.loyal_readers:
            analytics.fetch_followers()
            analytics.loyal_readers()
        if args.insights:
            analytics.fetch_followers()
            analytics.insights()
        if args.content_analysis:  analytics.content_analysis()
        if args.commenter_enrichment:
            analytics.fetch_followers()
            analytics.commenter_enrichment(args.enrich_top)
        if args.reading_list:      analytics.reading_list()
        if args.followed_tags:     analytics.followed_tags_analysis()
        if args.competitive_tags:  analytics.competitive_tags()
        if args.flare_tags:        analytics.fetch_articles_full()
        if args.tag_fix:           analytics.tag_fix_suggestions()

    if args.export_json: analytics.export_json(args.export_json, args.days)
    if args.export_csv:  analytics.export_csv(args.export_csv, args.days)


if __name__ == "__main__":
    main()
