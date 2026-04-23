---
project: DFC (Dave's Fishing Charters)
type: Static website + Python automation
last-updated: 2026-04-23
---

# DFC Wiki

Dave's Fishing Charters — Montague, Michigan. Personal project.
Static HTML website with Python-driven daily weather/wave reporting and PowerShell tooling.

## Pages

- [tools.md](tools.md) — All tools in `tools/` with usage and design notes
- [data-sources.md](data-sources.md) — Open-Meteo and NOAA NDBC API integration details
- [seo.md](seo.md) — SEO/AEO requirements and gap analysis tool

---

## Quick Facts

| Item | Value |
|------|-------|
| Path | `C:\GIT\DFC` |
| Remote | `https://github.com/Coopedak/DFC.git` |
| Site URL | `https://www.davesfishingcharters.com/` |
| Business | 5123 Osmun Street, Montague, Michigan 49437 |
| Phone | 231-672-0399 |
| Boat Launch | Montague Municipal Boat Launch, 8500 Ramp Rd, Montague, MI 49437 |
| Location Lat/Lon | 43.4148 / -86.3560 |
| Timezone | America/Detroit |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Site | Static HTML/CSS/JS |
| Automation | Python 3.13 (`tools/update_montague_report.py`) |
| Tooling | PowerShell 5.1 scripts in `tools/` |
| Scheduler | Windows Task Scheduler (daily 05:10) |
| Weather API | Open-Meteo (free, no key) |
| Buoy API | NOAA NDBC realtime2 text feed |
| Output | `data/montague_report_latest.json` + `montague-wave-report.html` |

---

## Tools

All tools live in `tools/`. PS5.1 compatible — no `?.`, no `--` em-dashes.

| Script | Purpose | Run |
|--------|---------|-----|
| `run_daily_report.ps1` | Entry point — invokes Python report | Manual or via Task Scheduler |
| `update_montague_report.py` | Main wave/weather report generator | `python tools/update_montague_report.py` |
| `install_daily_task.ps1` | Register Windows Scheduled Task | Admin PowerShell |
| `new_blog_post.ps1` | Scaffold a new blog post HTML + register | `.\tools\new_blog_post.ps1 -Slug slug -Title "..." -Description "..."` |
| `generate_blog_feed.ps1` | Regenerate `blog/rss.xml` from registry | Auto-called by `new_blog_post.ps1` |
| `seo_gap_analysis.ps1` | Audit all HTML files for SEO fields | `.\tools\seo_gap_analysis.ps1` |

---

## Key Data Paths

| Path | Purpose |
|------|---------|
| `data/montague_report_latest.json` | Last successful report JSON |
| `data/report_logs/report.log` | Append-only execution log |
| `data/.report.lock` | 30-minute lock file (prevents overlapping runs) |
| `blog/posts/registry.json` | Blog post registry (slug, title, description, date, url) |
| `blog/rss.xml` | RSS feed (regenerated on each new post) |
| `montague-wave-report.html` | Live HTML report output |

---

## Report Logic (`update_montague_report.py`)

1. Acquires lock file (`data/.report.lock`) — skips if fresh lock exists (< 30 min)
2. Fetches wave/weather from **Open-Meteo** (marine + forecast APIs)
3. Fetches wave data from **NOAA NDBC** buoys — tries stations `45029, 45161, MKGM4, 45167, 45024` in order
4. Averages available source data
5. Falls back to previous JSON if all sources fail (marks `stale: true`)
6. Writes atomic JSON (`data/montague_report_latest.json`) and regenerated HTML (`montague-wave-report.html`)

**Wave condition thresholds:**
| Feet | Label |
|------|-------|
| < 1.5 | Calm |
| 1.5–3.0 | Light chop |
| 3.0–4.5 | Moderate chop |
| 4.5–6.0 | Rough |
| >= 6.0 | Very rough |

---

## Blog Tooling

`new_blog_post.ps1` creates a full SEO-complete HTML scaffold at `blog/posts/{slug}.html`:
- Canonical URL, OG tags, Twitter card, JSON-LD BlogPosting schema
- Registers entry in `blog/posts/registry.json`
- Auto-calls `generate_blog_feed.ps1` to update RSS

`generate_blog_feed.ps1` reads `registry.json` and outputs RFC-2822-dated RSS items.

---

## SEO Requirements (per `seo_gap_analysis.ps1`)

Every HTML page must have:
- `<title>` tag
- `<meta name="description">`
- `<link rel="canonical">`
- `<h1>` element
- `<script type="application/ld+json">` (JSON-LD structured data)

Sitemap must include both `blog/` and `montague-wave-report.html` entries.

---

## Session Log

| Date | What happened | Tool |
|------|--------------|------|
| 2026-04-23 | Initial wiki created by Loop 14 knowledge extraction | Claude Sonnet 4.6 |
