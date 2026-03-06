# Repository Guidelines

## Project Structure & Module Organization
This repository is a static multi-page site. Root-level HTML files are page entry points (`index.html`, `contact.html`, `rates.html`, `destinations.html`, and `*-to-montague-fishing-charter.html`). Shared styling and scripts live in `assets/css/styles.css` and `assets/js/main.js`. Discovery files are `sitemap.xml`, `robots.txt`, and `llms.txt`.

## Build, Test, and Development Commands
- `cd C:\GIT\DFC`
- `python -m http.server 8080` runs the site locally at `http://localhost:8080`.
- `rg -n "pattern" C:\GIT\DFC` checks metadata/content quickly.
- `Get-ChildItem C:\GIT\DFC -Filter *.html` lists page files for QA sweeps.
- `powershell -ExecutionPolicy Bypass -File .\tools\generate_blog_feed.ps1` regenerates the blog RSS feed after new posts land.

## Coding Style & Naming Conventions
Use UTF-8 text, 2-space HTML/CSS indentation, and descriptive, lowercase kebab-case filenames (example: `toledo-to-montague-fishing-charter.html`). Keep metadata accurate and human-readable (no placeholders). Keep shared styles in `assets/css/styles.css`; avoid inline styles unless narrowly scoped.

## Testing Guidelines
No formal test framework is configured. Required manual QA for every major change:
- Validate all internal links.
- Validate title/meta/OG/Twitter tags per page.
- Validate JSON-LD schema consistency.
- Validate sitemap/robots/llms updates.
- Check desktop + mobile rendering.

## Security & Configuration Tips
Do not expose secrets in static files. Keep contact forms configured to approved endpoints only. Never publish private keys, tokens, or admin URLs in markup.

## GBP, SEO, and AEO Compliance Rules (Mandatory)
- Keep one real GBP business address: **5123 Osmun Street, Montague, Michigan 49437**.
- Keep launch location separate in content: **Montague Municipal Boat Launch, 8500 Ramp Rd, Montague, MI 49437**.
- Do not create fake city offices, virtual offices, or misleading local claims.
- Destination SEO must position travelers coming to Montague, not the business operating from their city.

## Must-Do After Big Plan Execute
Run a compliance gap analysis before and after major work against Google Search Essentials, Google spam policies, GBP representation rules, and Bing webmaster guidance. Use `powershell -ExecutionPolicy Bypass -File .\tools\seo_gap_analysis.ps1`. If any check fails, stop release, fix, and re-validate.

## Commit & Pull Request Guidelines
If/when Git is initialized, use concise conventional commits (example: `feat: add columbus destination page`, `fix: correct city meta descriptions`). PRs should include: summary, changed files, compliance notes (GBP/SEO/AEO), and screenshots for visual updates.
