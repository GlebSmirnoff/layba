# FRONTEND_ROUTES.md — карта Next.js App Router (страницы/лейауты/route handlers)

> Обновляй перед новым чатом. Показывает, какие `page.tsx`, `layout.tsx`, `route.ts` уже существуют.

## Как обновить (PowerShell, из КОРНЯ репо)
```powershell
"Layba — frontend routes (src/app)" | Out-File -Encoding utf8 .\docs\maps\FRONTEND_ROUTES.md
Get-ChildItem .\frontend\src\app -Recurse -File `
  | Where-Object { $_.Name -match '^(page|layout|route)\.(tsx|ts)$' } `
  | ForEach-Object { $_.FullName.Substring((Resolve-Path .).Path.Length+1) } `
  | Sort-Object `
  | Out-File -Append -Encoding utf8 .\docs\maps\FRONTEND_ROUTES.md
```

## Текущая карта (вставь вывод сюда)
```
<вставь сюда результат команды выше>
```
