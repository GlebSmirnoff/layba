# ROOT_TREE.md — верхнеуровневое дерево репозитория (DEV-снимок)

> Обновляй перед новым чатом. Снимок нужен, чтобы агент видел *общую структуру* и не лез не туда.

## Как обновить (Windows PowerShell, запустить из КОРНЯ репо)
```powershell
# создаём папку, если нет
mkdir docs\maps -Force | Out-Null
# перезаписываем файл
"Layba — repo root (short list)" | Out-File -Encoding utf8 .\docs\maps\ROOT_TREE.md
(Get-ChildItem -Name) | Sort-Object | Out-File -Append -Encoding utf8 .\docs\maps\ROOT_TREE.md
```

## Текущий снимок (вставь вывод сюда)
```
<вставь сюда результат команды выше>
```
