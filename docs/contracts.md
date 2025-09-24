OpenAPI — источник правды и генерация клиентов (web/mobile)
Цель

OpenAPI-схема — единственный источник правды по API. Любые изменения в бэке → обновляем схему → регенерируем клиентов → проверяем сборку. В PR всегда виден дифф openapi.yaml.

Источник правды

Публичная схема: GET /api/schema (DRF Spectacular).

Артефакт в репозитории: shared/contracts/openapi.yaml (версионируется).

Формат: OpenAPI 3.0+ (совместим с openapi-typescript, orval, Swagger UI).

Экспорт схемы из бэка
# Бэк запущен на :8000
curl http://backend.localhost/api/schema -o shared/contracts/openapi.yaml

Регламент изменений API

Внесли изменения в DRF-ручки / сериализаторы / схемы.

Пересобрали схему и обновили shared/contracts/openapi.yaml.

Регенерировали клиентов (web/mobile).

Убедились, что типы собираются (typecheck), фронты компилятся.

В PR приложили:

дифф shared/contracts/openapi.yaml,

краткий список затронутых SDK-файлов (если менялись).

Локации клиентов и регенерация
Web (Next.js)

Типы: frontend/src/api/schema.ts

Генерация:

cd frontend
pnpm run gen:api
# (скрипт должен быть в package.json):
# "gen:api": "openapi-typescript ../shared/contracts/openapi.yaml -o src/api/schema.ts"

Mobile (Expo)

Типы: mobile/src/api/schema.ts

Генерация:

cd mobile
pnpm run gen:api
# "gen:api": "openapi-typescript ../shared/contracts/openapi.yaml -o src/api/schema.ts"

ENV и клиентские обёртки
Web

Базовый URL берём из NEXT_PUBLIC_API_BASE_URL (пример для dev):

NEXT_PUBLIC_API_BASE_URL=http://backend.localhost


Клиент добавляет credentials: 'include' и прокидывает X-Request-ID (если нужен) в логи/метрики.

Mobile

Базовый URL берём из API_BASE_URL_MOBILE (через app.config.ts → extra):

Android эмулятор: http://10.0.2.2:8000

iOS симулятор: http://127.0.0.1:8000

Физ. устройство: http://<IP_ПК>:8000

Правило auth для мобилы (на будущее): refresh-токен в SecureStore, access — в памяти.

CI-гейт (на этапе 0 подключим)

Идея пайплайна:

export-openapi — валидируем и кладём openapi.yaml как артефакт.

generate-clients — реген web/mobile клиентов.

lint/typecheck — проверяем типы и сборку фронтов.

Если API изменили, а схему не обновили / клиентов не перегенерили — билд падает.

Check-list (DoD блока Contracts)

 /api/schema доступен локально.

 shared/contracts/openapi.yaml обновлён и в репозитории.

 Сгенерены типы: frontend/src/api/schema.ts, mobile/src/api/schema.ts.

 Описан регламент в этом файле (и соблюдаем его в PR).

 ENV-ключи заданы: NEXT_PUBLIC_API_BASE_URL, API_BASE_URL_MOBILE.

Три частые проблемы и быстрые решения

CORS/credentials: для web включить CORS_ALLOW_CREDENTIALS=True и whitelists для frontend.localhost/localhost:3000.

“Failed to fetch” на web: проверь, что фронт реально слушает :3000, бэк — :8000, Traefik UP (8090) и host-правила на месте.

Mobile не видит localhost: для Android всегда 10.0.2.2, для iOS — 127.0.0.1, для девайса — IP ПК.

Быстрые команды

Экспорт схемы:

curl http://backend.localhost/api/schema -o shared/contracts/openapi.yaml


Регенерация типов:

cd frontend && pnpm run gen:api
cd ../mobile && pnpm run gen:api