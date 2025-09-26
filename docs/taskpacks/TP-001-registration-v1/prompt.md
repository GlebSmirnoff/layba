Ты — исполнитель по Layba. Работай строго по docs/Agents.md. Контекст бери из docs/context/capsule.md(.json) и карт docs/maps/FRONTEND_ROUTES.md, docs/maps/BACKEND_APPS.md. Задача: выполнить TP-001 Registration v1 по файлам README.md, interfaces.md, dod.md.

Сначала дай Change Plan: полный список файлов/путей, что именно правим/создаём (без кода).

Затем дай Пошаговый план из 6–10 микро‑шагов (каждый шаг: цель → выходной артефакт → как проверить).

Укажи команды проверки: как открыть Swagger, curl к ключевым ручкам, куда смотреть логи; smoke для Mailhog/MinIO/Traefik.

Приложи DoD чек‑лист (скопируй из dod.md) с полями для отметок.

NO‑TOUCH: infra/*, базовые middleware/settings, shared/contracts/openapi.yaml — только через процедуру экспорта из live /api/schema.

Кода не присылай, пока Change Plan не согласован.