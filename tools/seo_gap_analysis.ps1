$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$today = Get-Date -Format "yyyy-MM-dd HH:mm zzz"
$htmlFiles = Get-ChildItem -Path $root -Recurse -File -Include *.html

$required = @("title", "description", "canonical", "h1", "jsonld")
$missingRows = @()
foreach ($f in $htmlFiles) {
  $c = Get-Content $f.FullName -Raw
  $checks = [ordered]@{
    title = ($c -match "<title>.*?</title>")
    description = ($c -match '<meta\s+name="description"')
    canonical = ($c -match '<link\s+rel="canonical"')
    h1 = ($c -match "<h1[\s>]")
    jsonld = ($c -match "application/ld\+json")
  }
  $miss = $checks.GetEnumerator() | Where-Object { -not $_.Value } | Select-Object -ExpandProperty Key
  if ($miss.Count -gt 0) {
    $missingRows += [pscustomobject]@{
      File = $f.FullName.Replace("$root\", "")
      Missing = ($miss -join ", ")
    }
  }
}

$brokenRows = @()
foreach ($f in $htmlFiles) {
  $dir = Split-Path $f.FullName -Parent
  $content = Get-Content $f.FullName -Raw
  $matches = [regex]::Matches($content, '(?i)(?:href|src)="([^"]+)"')
  foreach ($m in $matches) {
    $u = $m.Groups[1].Value
    if ($u -match "^(https?:|mailto:|tel:|#|javascript:|data:)") { continue }
    if ($u.StartsWith("/")) { $target = Join-Path $root $u.TrimStart("/") } else { $target = Join-Path $dir $u }
    $targetNorm = $target.Split("?")[0].Split("#")[0]
    if (-not (Test-Path $targetNorm)) {
      $brokenRows += [pscustomobject]@{
        File = $f.FullName.Replace("$root\", "")
        Ref = $u
      }
    }
  }
}

$publicFiles = Get-ChildItem -Path $root -Recurse -File -Include *.html, *.xml, *.txt
$allText = ($publicFiles | ForEach-Object { Get-Content $_.FullName -Raw }) -join "`n"
$hasBusinessAddress = $allText -match [regex]::Escape("5123 Osmun Street")
$hasLaunchAddress = $allText -match [regex]::Escape("8500 Ramp Rd")
$fakeOfficeFlags = ([regex]::Matches($allText.ToLower(), "virtual office|coworking suite|mailbox rental")).Count

$sitemapPath = Join-Path $root "sitemap.xml"
$sitemapOk = $false
if (Test-Path $sitemapPath) {
  $sitemap = Get-Content $sitemapPath -Raw
  $sitemapOk = ($sitemap -match "blog/") -and ($sitemap -match "montague-wave-report\.html")
}

$summary = [pscustomobject]@{
  timestamp = $today
  html_files_scanned = $htmlFiles.Count
  missing_core_seo_count = $missingRows.Count
  broken_link_count = $brokenRows.Count
  gbp_business_address_present = $hasBusinessAddress
  launch_address_present = $hasLaunchAddress
  fake_office_phrase_hits = $fakeOfficeFlags
  sitemap_contains_blog_and_wave = $sitemapOk
}

"SEO/AEO Gap Analysis"
$summary | Format-List
if ($missingRows.Count -gt 0) {
  ""
  "Missing Core SEO Fields:"
  $missingRows | Sort-Object File | Format-Table -AutoSize
}
if ($brokenRows.Count -gt 0) {
  ""
  "Broken Local Links:"
  $brokenRows | Sort-Object File, Ref | Format-Table -AutoSize
}
