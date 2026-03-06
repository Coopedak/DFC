$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$registryPath = Join-Path $root "blog\posts\registry.json"
if (-not (Test-Path $registryPath)) { throw "Missing registry: $registryPath" }

$escapeXml = { param($text) if (-not $text) { return "" } ; return [System.Security.SecurityElement]::Escape($text) }
$entries = (Get-Content $registryPath -Raw | ConvertFrom-Json)
$entries = $entries | Sort-Object @{ Expression = { [DateTime]::ParseExact($_.date, "yyyy-MM-dd", $null) } } -Descending

$buildDate = (Get-Date).ToString("R")
$channelTitle = "Captain Dave Blog"
$channelDesc = "Fishing reports, trip tips, and Montague launch updates."
$channelLink = "https://www.davesfishingcharters.com/blog/"

$items = $entries | ForEach-Object {
  $itemDate = ([DateTime]::ParseExact($_.date, "yyyy-MM-dd", $null)).ToString("R")
  $title = & $escapeXml $_.title
  $description = $_.description
  $link = $_.url
  @"
  <item>
    <title>$title</title>
    <link>$link</link>
    <description><![CDATA[$description]]></description>
    <pubDate>$itemDate</pubDate>
    <guid isPermaLink="true">$link</guid>
  </item>
"@
}

 $rss = @"
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>$channelTitle</title>
    <link>$channelLink</link>
    <description>$channelDesc</description>
    <language>en-US</language>
    <lastBuildDate>$buildDate</lastBuildDate>
    <atom:link href="https://www.davesfishingcharters.com/blog/rss.xml" rel="self" type="application/rss+xml" />
$( $items -join "`n")
  </channel>
</rss>
"@

$feedPath = Join-Path $root "blog\rss.xml"
Set-Content $feedPath $rss -Encoding UTF8
Write-Output "Generated $feedPath"
