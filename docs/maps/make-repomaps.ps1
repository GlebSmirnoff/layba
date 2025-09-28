# scripts\make-repomaps.ps1 — пересобирает все карты в docs\maps
param(
  [string]$RepoRoot = "."
)

Set-Location -Path $RepoRoot

# ensure folder
New-Item -ItemType Directory -Force -Path ".\docs\maps" | Out-Null

# ROOT_TREE
"Layba — repo root (short list)" | Out-File -Encoding utf8 .\docs\maps\ROOT_TREE.md
(Get-ChildItem -Name) | Sort-Object | Out-File -Append -Encoding utf8 .\docs\maps\ROOT_TREE.md

# FRONTEND_ROUTES
"Layba — frontend routes (src/app)" | Out-File -Encoding utf8 .\docs\maps\FRONTEND_ROUTES.md
if (Test-Path .\frontend\src\app) {
  Get-ChildItem .\frontend\src\app -Recurse -File `
    | Where-Object { $_.Name -match '^(page|layout|route)\.(tsx|ts)$' } `
    | ForEach-Object { $_.FullName.Substring((Resolve-Path .).Path.Length+1) } `
    | Sort-Object `
    | Out-File -Append -Encoding utf8 .\docs\maps\FRONTEND_ROUTES.md
} else {
  "frontend/src/app not found" | Out-File -Append -Encoding utf8 .\docs\maps\FRONTEND_ROUTES.md
}

# BACKEND_APPS
"Layba — backend urls.py map" | Out-File -Encoding utf8 .\docs\maps\BACKEND_APPS.md
if (Test-Path .\backend) {
  Get-ChildItem .\backend -Recurse -Filter urls.py `
    | ForEach-Object { $_.FullName.Substring((Resolve-Path .).Path.Length+1) } `
    | Sort-Object `
    | Out-File -Append -Encoding utf8 .\docs\maps\BACKEND_APPS.md
} else {
  "backend folder not found" | Out-File -Append -Encoding utf8 .\docs\maps\BACKEND_APPS.md
}

# MOBILE_TREE
"Layba — mobile src tree" | Out-File -Encoding utf8 .\docs\maps\MOBILE_TREE.md
if (Test-Path .\mobile\src) {
  Get-ChildItem .\mobile\src -Recurse `
    | ForEach-Object { $_.FullName.Substring((Resolve-Path .).Path.Length+1) } `
    | Sort-Object `
    | Out-File -Append -Encoding utf8 .\docs\maps\MOBILE_TREE.md
} else {
  "mobile/src not found" | Out-File -Append -Encoding utf8 .\docs\maps\MOBILE_TREE.md
}

Write-Host "Repo maps updated => docs\maps"
