# Changelog

All notable changes to devto-analytics-pro are documented here.

---

## [2.0.0] — 2026-06-06

Major feature expansion. 14 new analysis commands added. The CLI now covers the full
accessible surface of the DEV.to API including audience intelligence, content analysis,
tag optimisation, and competitive positioning.

### New commands

**Audience**
- `--commenters` — ranks all commenters across your articles by frequency, surfaces power
  commenters (3+ articles), strips your own replies automatically via `/api/users/me`
- `--loyal-readers` — cross-references commenter list against your 4,000+ follower list;
  finds followers who comment, commenters who haven't followed yet (conversion ops),
  and early adopters (followed before your growth inflection)
- `--commenter-enrichment` — hits `/api/users/by_username` for each top commenter;
  returns GitHub handle, Twitter, website, DEV join date, follower membership status
- `--follower-correlation` — bins follower join timestamps by ISO week, overlays publish
  events as an ASCII bar chart; surfaces which articles drove follower spikes

**Content**
- `--content-analysis` — fetches full `body_markdown` for all articles; outputs word count
  distribution, vocabulary richness, avg sentence length, title-length-vs-views correlation,
  word-count-vs-views correlation, top tech/tool mentions (regex-matched, false-positive-safe),
  flare tag distribution, edit history, and external/internal link density
- `--series` — detects multi-part article series by title heuristic (Part N, Ep N, Vol N,
  trailing number); outputs per-series reader retention (view drop-off part 1 → last)
- `--tag-fix` — scans article `body_markdown` with 19 signal patterns; diffs against current
  tags; outputs per-article suggestions with direct DEV.to edit URLs and a global quick-wins
  summary sorted by combined views × articles affected

**Discovery**
- `--reading-list` — fetches your saved articles; shows tag consumption vs tag production,
  authors you read most, tags you consume but never write about, tags you write but never read
- `--followed-tags` — fetches tags you follow (tries `/follows/tags`, falls back to reading
  list inference); cross-references against writing tags; surfaces aligned, gap, and
  misaligned tag sets
- `--competitive-tags` — fetches top 5 current articles in each of your primary tags;
  shows reaction counts, publish dates, authors; flags your own articles with `← YOU`

**Timing & reach**
- `--publish-heatmap` — day × hour heatmap of average views per publish slot rendered with
  Unicode block characters; lists top 5 slots with avg view counts
- `--cross-platform` — scans `canonical_url` fields; detects syndicated content; compares
  engagement rates native vs syndicated; estimates upstream reach
- `--flare-tags` — fetches public article view (`/articles?username=`) and merges `flare_tag`
  field into article objects for use by other commands

**Synthesis**
- `--insights` — synthesised intelligence report; pulls from all loaded data; outputs
  portfolio snapshot, ranked content strategy findings, top content by engagement and views,
  audience signal, and recommended next actions

### Changes to existing commands
- `--full-report` now includes all new commands in a single pass
- `--commenters` and `--loyal-readers` filter the authenticated user's own replies
  automatically using `/api/users/me`
- `--follower-correlation` spike attribution fixed — multi-article weeks now correctly
  attribute to the right article instead of the last one processed
- `--insights` 3-month trend calculation replaced with month-over-month delta logic

### Bug fixes
- `go`, `git`, `sha` false positives in content analysis fixed — all tech signals now
  use compiled word-boundary regex patterns instead of `str.count()`
- Reading list `tag_list` parsing fixed — handles both list and comma-string formats
  returned by the DEV.to readinglist endpoint
- `/followed_tags` 404 fixed — now tries three endpoint paths with correct v1 Accept
  header; falls back to reading list inference if all paths unavailable
- `page_views_count` was absent from public `/articles?username=` endpoint — confirmed
  as by design (private field); `--flare-tags` uses public endpoint only for `flare_tag`
  field and does not overwrite view counts

### New flag
- `--enrich-top N` — controls how many commenters `--commenter-enrichment` profiles
  (default: 15)

---

## [1.0.0] — 2025-10-22

Initial release.

- `--overview` — total views, reactions, comments, avg views, engagement rate
- `--top N` — top N articles sortable by views, reactions, comments, or engagement
- `--tags` — tag performance breakdown by total views, avg views, reactions, comments
- `--reading-time` — performance by reading time bucket (0-3m, 4-5m, 6-10m, 11-15m, 16m+)
- `--growth` — month-over-month publishing and engagement trend (last 12 months)
- `--underperformers` — articles below 50% avg views AND 50% avg engagement
- `--export-json` — full article data to JSON
- `--export-csv` — article data to CSV with engagement % column
- `--days N` — date filter applicable to most commands
- `--full-report` — runs all analysis commands in sequence

---

*devto-analytics-pro // badBANANA Research Collective // GnomeMan4201*
