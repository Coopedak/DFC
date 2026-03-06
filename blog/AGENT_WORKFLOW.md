# Blog Agent Workflow (Twice Monthly)

Schedule:
- Post 1 in week 1
- Post 2 in week 3

Before drafting:
1. Run GBP/SEO/AEO compliance gap check: `powershell -ExecutionPolicy Bypass -File .\tools\seo_gap_analysis.ps1`
2. Pick one real customer question/topic.
3. Define one primary query intent and one supporting intent.
4. Scaffold post with: `powershell -ExecutionPolicy Bypass -File .\tools\new_blog_post.ps1 -Slug "<slug>" -Title "<title>" -Description "<meta description>"`

Post requirements:
- 700-1200 words
- Quick answer in first paragraph
- 2 FAQ Q&A minimum
- One clear CTA to call/text 231-672-0399
- Mention Montague home-port context accurately
- Keep one real business address (5123 Osmun Street) and separate launch location (8500 Ramp Rd)

After publishing (must-do):
1. Add card in `blog/index.html`
2. Add post URL to `sitemap.xml`
3. Add post URL to `llms.txt`
4. Run recursive link check and metadata sanity scan
5. Regenerate the blog RSS feed: `powershell -ExecutionPolicy Bypass -File .\tools\generate_blog_feed.ps1`
