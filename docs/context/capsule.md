# Layba — Context Capsule (v0.1)

## Services & Ports (dev)
- Traefik: dashboard http://127.0.0.1:8090
- Backend (Django): http://backend.localhost  → :8000
- Frontend (Next.js): http://frontend.localhost → :3000
- Postgres 16: localhost:5432 (docker volume: layba-dev_pgdata)
- Redis 7: localhost:6379
- MinIO: API :9000, Console :9001 (bucket: **TBD/layba-dev**)
- Mailhog UI: http://localhost:8025

## API / Contracts
- Live schema: `GET /api/schema` (DRF Spectacular)
- Artifact: `shared/contracts/openapi.yaml` (источник для генераторов)
- Генерация клиентов:
  - Web: `cd frontend && pnpm run gen:api` → `src/api/schema.ts`
  - Mobile: `cd mobile && pnpm run gen:api` → `src/api/schema.ts`
- Дифф схемы обязателен в PR при изменении API.

## Frontends
- **Web**: Next.js (App Router, TS). Страницы: `/healthz`. Base URL: `NEXT_PUBLIC_API_BASE_URL=http://backend.localhost`
- **Mobile**: Expo (TS), экраны: **Health**, i18n EN/UK/PL, React Query. Base URL: `API_BASE_URL_MOBILE`  
  - Android эмулятор: `http://10.0.2.2:8000`  
  - iOS симулятор: `http://127.0.0.1:8000`  
  - Device: `http://<IP_PC>:8000`

## Auth (план/состояние)
- Web (Этап 0): cookie-сессии + CSRF; `SameSite=Lax` (dev), `CORS_ALLOW_CREDENTIALS=true`.
- Mobile (дальше): JWT — refresh в SecureStore, access в памяти.
- Статусы сейчас: login/logout — **заглушки в планах** (Этап 0 День 2).

## Security (dev baseline)
- CORS: разрешены `frontend.localhost`, `localhost:3000` (credentials=true).
- CSRF: будет включён на Этапе 0 (эндпойнт `/csrf/`).
- Заголовок `X-Request-ID`: логируем/пробрасываем клиентами (план).
- Rate limits, password policy, 2FA — **позже** (добавим TP).

## Data Stores
- **Postgres**: основная БД (схемы TBD по доменам: wallet/listing/auction/...).
- **Redis**: кеш/сеансы/фьючер-очереди (Celery/RQ — позже).
- **MinIO**: файлы и медиа (bucket имя зафиксировать и добавить в `.env.example`).
- CDN/пресайнинг — **позже**.

## Observability
- Логи: dev-уровень (консоль).  
- План: Sentry (web/mobile/backend), базовый OpenTelemetry/metrics позже.
- Health endpoints уже есть: `/healthz`, `/readiness`.

## Delivery / CI
- Сейчас: локальная dev-среда (Docker Desktop).  
- CI-гейт по контрактам: **подключим на Этапе 0** (export → generate → typecheck).
- Релизы (stage/prod): позже; Traefik пока только локально.

## Conventions / No-Touch
- Не трогаем без TP: `infra/*`, базовые middleware/settings, `shared/contracts/openapi.yaml` (только через процедуру).
- Ветки: `feat/...`, `chore/...`, `docs/...`; PR → Squash & Merge + Delete branch.

## Быстрые команды
```powershell
# Инфра
cd infra; .\dev-up.ps1
# Экспорт схемы и реген клиентов
curl http://backend.localhost/api/schema -o shared/contracts/openapi.yaml
cd frontend; pnpm run gen:api
cd ..\mobile; pnpm run gen:api
