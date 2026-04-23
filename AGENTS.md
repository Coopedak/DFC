# AGENTS.md — DFC

Universal agent instructions. Recognized by Claude Code, OpenAI Codex CLI, and others.

---

## Read First

1. `C:\GIT\ai-optimization\llms.txt` — framework manifest
2. `llms.txt` — this project's context

---

## Mandatory Rules

### PowerShell Scripts
- All tools live in `tools/` — PS5.1 compatible (no `?.`, no em-dashes `--`)
- Daily report automation: `run_daily_report.ps1`
- SEO analysis: `seo_gap_analysis.ps1`
- Blog tooling: `new_blog_post.ps1`, `generate_blog_feed.ps1`
- Montague report: `update_montague_report.py`

### PS5.1 Compatibility
- No null-conditional `?.` operator
- No em-dash `--` (use `-` instead)
- Use `[System.IO.File]::WriteAllText()` for BOM-free UTF-8 writes

### Session End
- Session review runs via Loop 13 nightly -- do not invoke /session-reviewer manually

---

## Self-Healing Protocol

When a task fails:
1. Check PS5.1 compatibility — null-conditional and em-dash operators are PS7+ only
2. If script fails: verify PowerShell version and module availability
3. Escalate: fail twice at Mid → Top for automation architecture decisions

Full protocol: `C:\GIT\ai-optimization\methodology\self-healing-loop.md`

---

## Model Tiers

- **Low** (haiku): reading existing scripts, documentation, simple edits
- **Mid** (sonnet): script development, report automation, SEO analysis — default
- **Top** (opus): new automation pipeline design, major architecture decisions

> Master index: `C:\GIT\ai-optimization\methodology\ai-workflow.md`
