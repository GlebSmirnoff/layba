Источник правды: /api/schema (DRF Spectacular). Любое изменение ручек → экспорт схемы → обновление openapi.yaml → реген клиентов.

Web-сессии (куки + CSRF)

POST /auth/session/login — логин (куки HttpOnly; CSRF на dev включён).

POST /auth/session/logout — логаут (очистка куки, инвалидируем сессию).

GET  /profile/me — профиль текущего пользователя; используется как guard для защищённых маршрутов.

GET  /csrf/ — вспомогательный (устанавливает csrftoken в cookie).

Mobile (Bearer + refresh)

POST /m/auth/token — получить access/refresh.

POST /m/auth/refresh — обмен refresh→access.

POST /m/auth/revoke — инвалидировать refresh.

Phone

POST /auth/phone/send_code — выдать код по телефону (rate limit 5/час на номер/IP).

POST /auth/phone/verify — проверить код; при успехе — аутентификация и доступ к guard-роутам.

Email

POST /auth/email/send_code — отправить код подтверждения email (dev через Mailhog).

POST /auth/email/confirm — подтвердить email по коду (единый формат «code»).

OAuth2

POST /auth/social/google   — вход по code (OAuth2 Authorization Code).

POST /auth/social/facebook — вход по access_token.

POST /auth/social/apple    — вход по id_token.

Moderator

GET  /api/notifications/settings/ — получить настройки уведомлений модератора.

PUT  /api/notifications/settings/ — обновить (только role="moderator").

Health / Schema (для smoke)

GET /healthz — проверка живости.

GET /api/schema — актуальная OpenAPI-схема.

Формат ошибок (суммарно)

{
  "code": "validation_error|unauthorized|forbidden|not_found|...",
  "message": "краткое описание",
  "details": { "field": ["msg", ...] },
  "request_id": "<uuid>"
}

Ограничения и политика

CORS dev: разрешены frontend.localhost и localhost:3000, credentials=true.

Web: авторизация через cookie-сессию + CSRF; Mobile: Bearer+refresh.

Секреты провайдеров OAuth — только через ENV (в репо не храним).