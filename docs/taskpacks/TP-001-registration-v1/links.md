Dev‑стенд (локально):

Mailhog UI — http://localhost:8025

MinIO — API http://localhost:9000, Console http://localhost:9001

Traefik Dashboard — http://127.0.0.1:8090

Backend:

База URL: http://backend.localhost

Health: GET /healthz

Schema: GET /api/schema (артефакт: shared/contracts/openapi.yaml)

Frontend:

База URL: http://frontend.localhost

Защищённые маршруты: /dashboard, /moderator/settings

Команды (из корня проекта):

Инфра: cd infra && ./dev-up.ps1 / ./dev-down.ps1 / ./dev-logs.ps1 / ./dev-reset.ps1

Экспорт схемы: curl http://backend.localhost/api/schema -o shared/contracts/openapi.yaml

Генерация клиентов: cd frontend && pnpm run gen:api / cd mobile && pnpm run gen:api

