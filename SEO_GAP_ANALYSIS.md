# SEO/AEO Gap Analysis Baseline

Last run: 2026-03-05 (America/New_York)

## Current Status
- HTML files scanned: 24
- Missing core SEO fields: 0
- Broken local links: 0
- GBP business address present: `5123 Osmun Street, Montague, Michigan 49437`
- Launch location present and separate: `Montague Municipal Boat Launch, 8500 Ramp Rd, Montague, MI 49437`
- Fake office phrase hits in public site files: 0
- Sitemap includes key discovery pages (blog + wave report): yes

## Google/Bing Compliance Guardrails
- Keep one real GBP location only: `5123 Osmun Street, Montague, Michigan 49437`.
- Keep launch point separate in content and trip logistics.
- Do not publish fake city offices, PO-box-as-office claims, or misleading locality statements.
- Destination pages must position visitors traveling to Montague (not services operating from their city).

## Runbook (Must Do After Major Changes)
1. Run:
   `powershell -ExecutionPolicy Bypass -File .\tools\seo_gap_analysis.ps1`
2. Fix all missing core SEO fields and broken links before release.
3. Re-check sitemap and `llms.txt` for any new page.
4. Verify LocalBusiness schema address matches GBP exactly.
5. Verify mobile nav, hero CTA, contact form, and blog links manually in local browser.

## Priority Opportunities (Phase 3)
- Add fresh photo gallery page instead of redirect to improve trust/E-E-A-T signals.
- Add `BlogPosting` schema to each new post using the same author/publisher pattern.
- Keep weather/wave report publishing daily to strengthen local relevance.
- Publish two authentic posts monthly focused on Montague launch conditions and regional travel-to-Montague intent.
