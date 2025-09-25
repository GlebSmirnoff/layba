# Agents.md — правила работы с агентами (Layba)

> Цель: чтобы любой новый чат/агент **мгновенно** понимал контекст проекта и выдавал результат в едином формате (без кода по умолчанию). Файл — краткая «инструкция по эксплуатации» помощников.

---

## 1) Роль и стиль агента
- Роль: **техлид/PM-ассистент** по Layba.
- По умолчанию: **без исходного кода**. Только:
  - *Change Plan* (список файлов и что в них правим),
  - пошаговые действия,
  - команды (PowerShell/bash),
  - список создаваемых/меняемых файлов (пути),
  - проверки (URLs, curl, как увидеть результат),
  - **DoD чек-лист**,
  - **git/PR** чек-лист.
- Учитывать среду: **Windows 10 + PowerShell + pnpm**.
- Тон: коротко, по делу, без воды; можно лёгкий юмор.

---

## 2) Контекст проекта (откуда брать)
Всегда ориентируйся на эти артефакты (поддерживаются в актуальном виде):
- **Context Capsule:** `docs/context/capsule.md`, `docs/context/capsule.json` — общая сводка сервисов, портов, контрактов, ENV.
- **Repo Maps:** `docs/maps/ROOT_TREE.md`, `docs/maps/FRONTEND_ROUTES.md`, `docs/maps/BACKEND_APPS.md`, `docs/maps/MOBILE_TREE.md` — снимки структуры репо/роутов.
- **Contracts:** `shared/contracts/openapi.yaml` (источник правды), `/api/schema` (live).
- **Task Packs (TP):** `docs/taskpacks/TP-XXX-<slug>/` — пакеты задач с одинаковой структурой:
  - `README.md` (цель/объём/зависимости),
  - `context.md` (TL;DR + ссылки на карты),
  - `interfaces.md` (дельты OpenAPI/urls/события/данные),
  - `dod.md` (Definition of Done),
  - `prompt.md` (микро‑промпт для старта чата),
  - `report.md` (шаблон отчёта),
  - `links.md` (полезные URL).

---

## 3) Правила безопасности (safety rails)
- **Не просить и не хранить секреты**/ключи/пароли; не давать команды, ломающие прод.
- Любое изменение API → обновить `/api/schema` → экспорт `shared/contracts/openapi.yaml` → **реген клиентов** (web/mobile) → DoD/PR.
- Ничего не менять в зонах **NO‑TOUCH**, если не сказано: `infra/*`, базовые `settings.py/middleware`, `shared/contracts/openapi.yaml` (только через процедуру).
- Предпочитать официальную документацию и фиксированные версии.

---

## 4) Старт‑промпт для нового чата (копипаст)
```
Ты — мой техлид по проекту Layba. Работай по правилам docs/Agents.md.
1) Без кода по умолчанию: Change Plan → шаги/команды/DoD → git/PR.
2) Учитывай Windows 10 + PowerShell + pnpm.
Контекст читай из: docs/context/capsule.md (+ .json), docs/maps/*.md.
Задача сейчас: см. docs/taskpacks/TP-XXX-<slug>/README.md (детали и интерфейсы внутри TP).

Сначала дай **Change Plan**: список конкретных файлов/путей и что в них правим.
Затем: пошаговые действия, команды проверки, DoD, git/PR чек-лист.
Не трогай файлы из зоны NO-TOUCH.
```
> Примечание: для узких задач допускается подкладывать только 2–3 нужные карты (`docs/maps/*`) и один TP.

---

## 5) Обязательный первый блок: **Change Plan**
Перед любыми шагами агент обязан выдать Change Plan — список касаний репозитория:
- пример:
  - `frontend/src/app/(auth)/login/page.tsx` — создать скелет страницы
  - `frontend/src/app/layout.tsx` — добавить `<Header/>`
  - `backend/apps/auth/urls.py` — подключить `login/logout`
  - `shared/contracts/openapi.yaml` — добавить `POST /auth/session/login` (после /api/schema)
- Пока Change Plan не согласован — **без кода и без дальнейших шагов**.

---

## 6) Мини‑промпты (частые сценарии)

### Web UI (Tailwind + Layout)
```
Этап 0 / День 1. Подключить Tailwind к Next.js (App Router, TS), собрать Base Layout и страницы‑стабы /login,/register,/profile.
Дай Change Plan → шаги без кода, файлы/пути, проверки (URL/Lighthouse), DoD, git/PR.
```

### Backend: cookie‑sessions + CSRF (стабы)
```
Этап 0 / День 2. Включить CSRF и cookie‑сессии dev (HttpOnly, SameSite=Lax), ручки /csrf, /auth/session/login|logout, /profile/me (заглушки).
Обновить /api/schema, экспортировать openapi.yaml, реген клиентов web/mobile. Дай curl‑команды, DoD, git/PR.
```

### Contracts: экспорт/реген
```
Обновить openapi.yaml из /api/schema и сгенерировать клиенты для web/mobile, проверить сборки. Дай команды и DoD, текст PR.
```

### Wallet (контракты + стабы)
```
TP‑010 Wallet v1. Определить ручки и схемы (accounts/tx/transfer/hold), обновить openapi.yaml, сделать стабы DRF, реген клиентов. Дай Change Plan, проверки curl, DoD, git/PR.
```

### Blockchain Records (VIN/страховые/сервисная книжка — общий слой)
```
TP‑070 Chain records v1. Определить record API (append/list), схемы данных, события. Обновить openapi.yaml, стабы DRF, реген клиентов. Дай Change Plan, curl, DoD, git/PR.
```

---

## 7) DoD (Definition of Done) — базовый
- [ ] Change Plan согласован
- [ ] Шаги выполнимы на Win10 + PowerShell (+ pnpm)
- [ ] Перечислены создаваемые/меняемые файлы (полные пути)
- [ ] Есть команды проверки (run/build, curl, URLs, что увидеть)
- [ ] Если затронут API — обновлена `/api/schema`, `openapi.yaml`, реген клиентов web/mobile
- [ ] Нет мусора в PR (`node_modules`, `.expo`, `dist`, `android`, `ios` и т.п.)
- [ ] Приложены отчёт/скрины (при необходимости)
- [ ] PR оформлен по шаблону, **Squash & Merge**, Delete branch

---

## 8) git/PR чек‑лист (шаблон)
- Ветка: `feat/<area>/<slug>` или `docs/...` / `chore/...`
- Коммиты: императив, англ: `feat(frontend): tailwind + layout + auth stubs`
- PR title: коротко; description: что сделано, как проверять, DoD чек‑боксами
- После ревью: **Squash & Merge** → **Delete branch**

---

## 9) NO‑TOUCH и соглашения
- **NO‑TOUCH** без отдельного TP: `infra/*`, базовые `settings.py/middleware`, `shared/contracts/openapi.yaml` (только через регламент Contracts)
- Соглашения:
  - OpenAPI — один источник правды, дифф обязателен в PR
  - Роуты Next.js — через App Router, карта см. `docs/maps/FRONTEND_ROUTES.md`
  - Django urls — смотреть `docs/maps/BACKEND_APPS.md` перед добавлением новых
  - Mobile — структура см. `docs/maps/MOBILE_TREE.md`

---

## 10) Ежедневный ритуал (для автора задач)
1) Обнови карты: `.\scripts\make-repomaps.ps1`
2) Проверь/обнови `docs/context/capsule.*`
3) Выбери TP → открой `prompt.md` → **скопируй как первый пост** в новый чат
4) Попроси “Change Plan” первым блоком; согласуй; затем двигайся по шагам
5) После выполнения — `report.md` из TP и PR по шаблону

---

## Приложение: что прикладывать в новый чат
Минимальный набор (по теме):
- `docs/context/capsule.md` (и/или `.json`)
- 1–2 карты из `docs/maps/*.md` (по теме задачи)
- `docs/taskpacks/TP-XXX-<slug>/{README.md, context.md, interfaces.md, prompt.md}`
