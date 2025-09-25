# MOBILE_TREE.md — важные папки Expo (src/*)

> Обновляй перед новым чатом. Агенту нужно видеть структуру экранов, i18n и библиотек.

## Как обновить (PowerShell, из КОРНЯ репо)
```powershell
"Layba — mobile src tree" | Out-File -Encoding utf8 .\docs\maps\MOBILE_TREE.md
Get-ChildItem .\mobile\src -Recurse `
  | ForEach-Object { $_.FullName.Substring((Resolve-Path .).Path.Length+1) } `
  | Sort-Object `
  | Out-File -Append -Encoding utf8 .\docs\maps\MOBILE_TREE.md
```

## Текущая карта (вставь вывод сюда)
```
<вставь сюда результат команды выше>
```
