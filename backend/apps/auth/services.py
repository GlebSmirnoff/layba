import logging
import random
from datetime import timedelta
from typing import Optional, Tuple

from django.utils import timezone

from .models import PhoneVerificationCode, EmailVerificationCode

# отдельные логгеры, чтобы в dev удобно фильтровать
log_sms = logging.getLogger("PHONE_SMS")
log_call = logging.getLogger("PHONE_CALL")
log_email = logging.getLogger("EMAIL_CODE")

TTL_MIN = 10
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
        raise PermissionError("unauthorized")

    rec.used = True
    rec.used_at = _now()
    rec.save(update_fields=["used", "used_at"])

    # в проекте используется легковесная «сессия-модель» пользователя
    # (без реальной БД-пользователей). Возвращаем dict.
    user = {
        "id": 1,
        "email": "phone-user@example.com",
        "role": "user",
    }
    return user, rec


# ----- EMAIL -----
def issue_email_code(email: str, ip: Optional[str], ua: Optional[str]) -> EmailVerificationCode:
    email = (email or "").strip().lower()

    existing = (
        EmailVerificationCode.objects.filter(
            email=email, used=False, expires_at__gt=_now()
        )
        .order_by("-created_at")
        .first()
    )
    if existing:
        return existing

    code = f"{random.randint(0, 999999):06d}"
    rec = EmailVerificationCode.objects.create(
        email=email,
        code=code,
        expires_at=_ttl(),
        used=False,
        attempts=0,
        ip=ip or "",
        ua=ua or "",
    )

    log_email.info("email_send_code to %s code=%s", _mask_email(email), code)
    return rec


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
        raise PermissionError("unauthorized")

    rec.used = True
    rec.used_at = _now()
    rec.save(update_fields=["used", "used_at"])

    user = {
        "id": 2,
        "email": email,
        "role": "user",
    }
    return user, rec
