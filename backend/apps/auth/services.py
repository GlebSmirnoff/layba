# backend/apps/auth/services.py
import logging
import os
import random
import secrets
from datetime import timedelta
from typing import Any, Dict, Optional, Tuple

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from .models import EmailVerificationCode, PhoneVerificationCode

# Отдельные логгеры, чтобы в dev удобно фильтровать
log_sms = logging.getLogger("PHONE_SMS")
log_call = logging.getLogger("PHONE_CALL")
log_email = logging.getLogger("EMAIL_CODE")
logger = logging.getLogger(__name__)
LOG_SEC = logging.getLogger("SEC")  # краткие безопасные логи (без токенов/PII)

DEV_SOCIAL_MOCK = os.getenv("DEV_SOCIAL_MOCK", "0") == "1"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")

TTL_MIN = 10
EMAIL_CODE_TTL_MIN = 10
MAX_ATTEMPTS = 5


# ----- helpers -----
def _now():
    return timezone.now()


def _ttl():
    return _now() + timedelta(minutes=TTL_MIN)


def _mask_phone(p: str) -> str:
    p = p or ""
    if len(p) <= 4:
        return "***"
    return f"{p[:2]}***{p[-2:]}"


def _mask_email(e: str) -> str:
    if not e:
        return "***"
    e = e.lower()
    try:
        local, domain = e.split("@", 1)
    except ValueError:
        return "***"
    local_m = (local[:1] + "***") if local else "***"
    domain_m = (domain[:1] + "***") if domain else "***"
    return f"{local_m}@{domain_m}"


def _send_email_code(email: str, code: str) -> None:
    subject = "Layba: ваш код подтверждения"
    body = f"Ваш код: {code}\nОн действует 10 минут."
    msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [email])
    msg.send(fail_silently=False)
    log_email.info("email_code_sent email=%s", _mask_email(email))


def issue_session_for(request, user: Dict[str, Any]) -> Dict[str, Any]:
    """
    user = {"id": int, "email": str, "role": "user"|"moderator"}
    """
    request.session["user"] = user
    request.session.modified = True
    return user


# ----- PHONE -----
def issue_phone_code(
    phone: str, method: str, ip: Optional[str], ua: Optional[str]
) -> PhoneVerificationCode:
    phone = phone.strip()
    method = (method or "sms").lower()

    existing = (
        PhoneVerificationCode.objects.filter(
            phone_e164=phone, method=method, used=False, expires_at__gt=_now()
        )
        .order_by("-created_at")
        .first()
    )
    if existing:
        # для idempotency возвращаем активную запись
        logger.info("phone_code_reuse phone=%s method=%s", _mask_phone(phone), method)
        return existing

    if method == "sms":
        code = f"{random.randint(0, 999999):06d}"
        last4 = None
    elif method == "call":
        code = None
        last4 = phone[-4:] if len(phone) >= 4 else None
    else:
        method = "sms"
        code = f"{random.randint(0, 999999):06d}"
        last4 = None

    rec = PhoneVerificationCode.objects.create(
        phone_e164=phone,
        method=method,
        code=code,
        last4_expected=last4,
        expires_at=_ttl(),
        used=False,
        attempts=0,
        ip=ip or "",
        ua=ua or "",
    )

    # dev-«отправка»
    if method == "sms" and code:
        log_sms.info("phone_send_code sms to %s code=%s", _mask_phone(phone), code)
    if method == "call" and last4:
        log_call.info(
            "phone_send_code call to %s expect_last4=%s", _mask_phone(phone), last4
        )
    logger.info("phone_code_issued phone=%s method=%s", _mask_phone(phone), method)
    return rec


def verify_phone_code(
    phone: str, code: Optional[str] = None, last4: Optional[str] = None
) -> Tuple[dict, PhoneVerificationCode]:
    phone = phone.strip()

    # определяем метод из входных полей
    if code:
        method = "sms"
        q = PhoneVerificationCode.objects.filter(
            phone_e164=phone, method="sms", used=False, expires_at__gt=_now()
        )
    else:
        method = "call"
        q = PhoneVerificationCode.objects.filter(
            phone_e164=phone, method="call", used=False, expires_at__gt=_now()
        )

    rec = q.order_by("-created_at").first()
    if not rec:
        raise ValueError("gone")  # истёк или не найден

    if rec.attempts >= MAX_ATTEMPTS:
        raise PermissionError("too_many_attempts")

    ok = False
    if method == "sms" and rec.code and code:
        ok = (rec.code or "").strip() == code.strip()
    if method == "call" and rec.last4_expected and last4:
        ok = (rec.last4_expected or "").strip() == last4.strip()

    if not ok:
        rec.attempts = rec.attempts + 1
        rec.save(update_fields=["attempts"])
        logger.info(
            "phone_verify_fail phone=%s method=%s attempts=%s",
            _mask_phone(phone),
            method,
            rec.attempts,
        )
        raise PermissionError("unauthorized")

    rec.used = True
    rec.used_at = _now()
    rec.save(update_fields=["used", "used_at"])
    logger.info("phone_verify_ok phone=%s method=%s", _mask_phone(phone), method)

    # В проекте сейчас используется легковесная «сессия-модель» пользователя
    user = {"id": 1, "email": "phone-user@example.com", "role": "user"}
    return user, rec


# ----- EMAIL -----
def issue_email_code(email: str, ip: str | None = None, ua: str | None = None) -> None:
    now = timezone.now()
    email_norm = (email or "").strip().lower()

    # пробуем реюзнуть активный код
    rec = (
        EmailVerificationCode.objects.filter(
            email=email_norm, used=False, expires_at__gt=now
        )
        .order_by("-created_at")
        .first()
    )

    if not rec:
        code = f"{random.randint(0, 999999):06d}"
        rec = EmailVerificationCode.objects.create(
            email=email_norm,
            code=code,
            expires_at=now + timedelta(minutes=EMAIL_CODE_TTL_MIN),
            ip=ip or "",
            ua=ua or "",
        )
        reuse = False
    else:
        reuse = True

    # ВАЖНО: отправляем письмо и при реюзе, и при создании
    _send_email_code(email_norm, rec.code)
    logger.info(
        "email_code_send reuse=%s email=%s", reuse, _mask_email(email_norm)
    )


def confirm_email_code(email: str, code: str) -> Tuple[dict, EmailVerificationCode]:
    email = (email or "").strip().lower()

    rec = (
        EmailVerificationCode.objects.filter(
            email=email, used=False, expires_at__gt=_now()
        )
        .order_by("-created_at")
        .first()
    )
    if not rec:
        raise ValueError("gone")

    if rec.attempts >= MAX_ATTEMPTS:
        raise PermissionError("too_many_attempts")

    if (rec.code or "").strip() != (code or "").strip():
        rec.attempts = rec.attempts + 1
        rec.save(update_fields=["attempts"])
        logger.info(
            "email_confirm_fail email=%s attempts=%s",
            _mask_email(email),
            rec.attempts,
        )
        raise PermissionError("unauthorized")

    rec.used = True
    rec.used_at = _now()
    rec.save(update_fields=["used", "used_at"])
    logger.info("email_confirm_ok email=%s", _mask_email(email))

    user = {"id": 2, "email": email, "role": "user"}
    return user, rec


# -------------------- GOOGLE --------------------
def google_exchange_code(
    code: str, redirect_uri: Optional[str], code_verifier: Optional[str]
) -> Dict[str, Any]:
    if DEV_SOCIAL_MOCK:
        # dev-имитация обмена: возвращаем фиктивный id_token
        return {
            "id_token": "dev-google-id-token",
            "access_token": "dev",
            "refresh_token": "dev",
        }
    # TODO: реальный обмен по OAuth token endpoint (PKCE при наличии code_verifier)
    raise NotImplementedError("Google exchange flow requires real credentials")


def google_verify_id_token(id_token: str) -> Dict[str, Any]:
    if DEV_SOCIAL_MOCK:
        # имитация расшифровки id_token
        return {
            "sub": "g_dev_123",
            "email": "google-user@example.com",
            "email_verified": True,
            "iss": "accounts.google.com",
            "aud": GOOGLE_CLIENT_ID,
        }
    # TODO: верификация по JWKS/Google lib, проверка aud/iss/exp
    raise NotImplementedError("Google verify requires real credentials")


# -------------------- FACEBOOK --------------------
def facebook_verify_access_token(access_token: str) -> Dict[str, Any]:
    if DEV_SOCIAL_MOCK:
        return {"id": "fb_dev_123", "email": "facebook-user@example.com"}
    # TODO: Graph /debug_token + /me?fields=id,email
    raise NotImplementedError("Facebook verify requires real credentials")

# -------------------- APPLE --------------------
def apple_verify_id_token(id_token: str) -> Dict[str, Any]:
    if DEV_SOCIAL_MOCK:
        return {
            "sub": "apple_dev_123",
            "email": "apple-user@example.com",
            "email_verified": True,
            "iss": "https://appleid.apple.com",
            "aud": APPLE_CLIENT_ID,
        }
    # TODO: верификация подписи по JWKS, проверка aud/iss/exp
    raise NotImplementedError("Apple verify requires real credentials")


# -------------------- FIND/CREATE USER --------------------
def find_or_create_user_from_social(payload: Dict[str, Any], provider: str) -> Dict[str, Any]:
    """
    В проекте пока нет полноценной таблицы пользователей — используем простую
    структуру для сессии. Если добавим модель User — тут будет поиск/создание.
    """
    email = payload.get("email") or f"{provider}-user@example.com"
    user = {"id": 1, "email": email, "role": "user"}
    LOG_SEC.info("social_login ok provider=%s email=%s", provider, _mask_email(email))
    return user
