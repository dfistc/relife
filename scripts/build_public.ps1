$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$public = Join-Path $root "public"

if (Test-Path -LiteralPath $public) {
    Remove-Item -LiteralPath $public -Recurse -Force
}

New-Item -ItemType Directory -Path (Join-Path $public "data") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $public "downloads") | Out-Null
Copy-Item -LiteralPath (Join-Path $root "index.html") -Destination $public
Copy-Item -LiteralPath (Join-Path $root "app.js") -Destination $public
Copy-Item -LiteralPath (Join-Path $root "styles.css") -Destination $public
Copy-Item -LiteralPath (Join-Path $root "data\papers.json") -Destination (Join-Path $public "data")
Copy-Item -Path (Join-Path $root "downloads\*.pdf") -Destination (Join-Path $public "downloads")
New-Item -ItemType File -Path (Join-Path $public ".nojekyll") | Out-Null

Write-Output "Public site built at $public"
