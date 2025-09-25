# BACKEND_APPS.md — карта Django apps/urls (где какие URL подключены)

> Обновляй перед новым чатом. Помогает не городить новые пути в неверных местах.

## Как обновить (PowerShell, из КОРНЯ репо)
```powershell
"Layba — backend urls.py map" | Out-File -Encoding utf8 .\docs\maps\BACKEND_APPS.md
Get-ChildItem .\backend -Recurse -Filter urls.py `
  | ForEach-Object { $_.FullName.Substring((Resolve-Path .).Path.Length+1) } `
  | Sort-Object `
  | Out-File -Append -Encoding utf8 .\docs\maps\BACKEND_APPS.md
```

## Дополнительно (по желанию): список Django apps (apps.py)
```powershell
Get-ChildItem .\backend -Recurse -Filter apps.py `
  | ForEach-Object { $_.FullName.Substring((Resolve-Path .).Path.Length+1) } `
  | Sort-Object
```

## Текущая карта (вставь вывод сюда)
```
<вставь сюда результат команды выше>
```
