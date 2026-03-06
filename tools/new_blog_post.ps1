param(
  [Parameter(Mandatory=$true)][string]$Slug,
  [Parameter(Mandatory=$true)][string]$Title,
  [Parameter(Mandatory=$true)][string]$Description,
  [string]$Date = (Get-Date -Format "MMMM d, yyyy")
)
$root = Split-Path $PSScriptRoot -Parent
$path = Join-Path $root ("blog\posts\" + $Slug + ".html")
if(Test-Path $path){ throw "Post exists: $path" }
$canon = "https://www.davesfishingcharters.com/blog/posts/$Slug.html"
$published = Get-Date $Date
$isoDate = $published.ToString("yyyy-MM-dd")
$pubDateRfc = $published.ToString("R")
$safeTitle = $Title.Replace('"', '&quot;')
$safeDescription = $Description.Replace('"', '&quot;')
$content = @"
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>$safeTitle | Captain Dave Blog</title>
  <meta name="description" content="$safeDescription" />
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="$safeTitle" />
  <meta property="og:description" content="$safeDescription" />
  <meta property="og:url" content="$canon" />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="$safeTitle" />
  <meta name="twitter:description" content="$safeDescription" />
  <link rel="stylesheet" href="../../assets/css/styles.css" />
  <link rel="canonical" href="$canon" />
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "$safeTitle",
    "description": "$safeDescription",
    "datePublished": "$isoDate",
    "dateModified": "$isoDate",
    "author": {"@type":"Person","name":"Captain Dave"},
    "publisher": {"@type":"Organization","name":"Dave's Fishing Charters","url":"https://www.davesfishingcharters.com/"},
    "mainEntityOfPage": "$canon",
    "about": {
      "@type":"Place",
      "name":"Montague Municipal Boat Launch",
      "address":{
        "@type":"PostalAddress",
        "streetAddress":"8500 Ramp Rd",
        "addressLocality":"Montague",
        "addressRegion":"MI",
        "postalCode":"49437",
        "addressCountry":"US"
      }
    }
  }
  </script>
</head>
<body>
<header>
  <div class="topbar">
    <div class="container topbar-inner">
      <div>Call today: <strong><a href="tel:+12316720399">231-672-0399</a></strong></div>
      <div><a href="../../contact.html">Book your trip</a> | Business Address: 5123 Osmun Street, Montague, Michigan 49437</div>
    </div>
  </div>
  <div class="container navbar">
    <a class="brand" href="../../index.html">Dave's Fishing Charters</a>
    <nav aria-label="Primary">
      <ul>
        <li><a href="../../index.html">Home</a></li>
        <li><a href="../../services.html">Services</a></li>
        <li><a href="../../montague-wave-report.html">Wave Report</a></li>
        <li><a href="../../destinations.html">Travelers</a></li>
        <li><a href="../index.html">Blog</a></li>
        <li><a href="../../contact.html">Contact</a></li>
      </ul>
    </nav>
  </div>
</header>
<main class="section">
  <div class="container">
    <h1>$safeTitle</h1>
    <p><small>Published: $Date</small></p>
    <p class="lead">Quick answer first. keep it plain and useful.</p>
    <h2>What this means for your trip to Montague</h2>
    <p>Explain what changed, what to expect, and how to plan launch day.</p>
    <h2>Simple game plan</h2>
    <ul class="list">
      <li>Best launch window</li>
      <li>Weather and wave watch notes</li>
      <li>What to bring and what to skip</li>
    </ul>
    <h2>FAQ</h2>
    <p><strong>Question?</strong> Answer in one short paragraph.</p>
  </div>
</main>
<footer><div class="container"><p class="small">&copy; <span data-year></span> Dave's Fishing Charters</p></div></footer>
<script src="../../assets/js/main.js"></script>
</body>
</html>
"@
Set-Content $path $content -Encoding UTF8
Write-Output "Created $path"

$registryPath = Join-Path $root "blog\posts\registry.json"
if(Test-Path $registryPath){
  $registry = Get-Content $registryPath -Raw | ConvertFrom-Json
} else {
  $registry = @()
}
if($registry | Where-Object { $_.slug -eq $Slug }) {
  throw "Registry entry already exists for $Slug"
}
$entry = [ordered]@{
  slug = $Slug
  title = $Title
  description = $Description
  date = $isoDate
  url = $canon
}
$registry += $entry
$registry | Sort-Object @{Expression={Get-Date $_.date}} -Descending | ConvertTo-Json -Depth 5 | Set-Content $registryPath -Encoding UTF8

$feedScript = Join-Path $root "tools\generate_blog_feed.ps1"
if(Test-Path $feedScript){
  & "$feedScript"
}
