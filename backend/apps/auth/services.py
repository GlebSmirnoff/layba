import logging
import random
import re
from dataclasses import dataclass
from typing import Optional, Tuple

from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from .models import PhoneVerificationCode, EmailVerificationCode

logger_sms = logging.getLogger("PHONE_SMS")
logger_call = logging.getLogger("PHONE_CALL")
logger_email = logging.getLogger("EMAIL_CODE")

E164_RE = re.compile(r"^\+[1-9]\d{6,14}$")
TTL_MINUTES = 10
MAX_ATTEMPTS = 5


def _mask(phone: str) -> str:
    # +380******123
    return phone[:-3].replace(phone[4:-3], "*" * max(0, len(phone[4:-3]))) + phone[-3:]


def _generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


@dataclass
class IssueResult:
    record: PhoneVerificationCode
    created: bool


def issue_phone_code(*, phone: str, method: str, ip: Optional[str], ua: Optional[str]) -> IssueResult:
    if not E164_RE.match(phone):
        raise ValueError("Invalid E.164 phone")

    now = timezone.now()
    expires_at = now + timezone.timedelta(minutes=TTL_MINUTES)

    # reuse active not-used code for the same phone/method
    existing = (
        PhoneVerificationCode.objects.filter(
            phone_e164=phone, method=method, used=False, expires_at__gt=now
        )
        .order_by("-created_at")
        .first()
    )
    if existing:
        rec = existing
        created = False
    else:
        rec = PhoneVerificationCode(
            phone_e164=phone,
            method=method,
            expires_at=expires_at,
            ip=ip,
            ua=ua[:256] if ua else None,
        )
        if method == PhoneVerificationCode.Method.SMS:
            rec.code = _generate_code()
        else:
            # CALL: ожидаем последние 4 цифры
            hint = getattr(settings, "DEV_FAKE_CALLER_LAST4", None)
            rec.last4_expected = hint or phone[-4:]
        rec.save()
        created = True

    # dev "sending"
    if method == PhoneVerificationCode.Method.SMS:
        logger_sms.info("send sms code=%s to %s", rec.code, _mask(phone))
    else:
        logger_call.info("expect last4=%s for %s", rec.last4_expected, _mask(phone))

    return IssueResult(record=rec, created=created)


@dataclass
class VerifyResult:
    ok: bool
    reason: Optional[str]
    user_payload: Optional[dict]


@transaction.atomic
def verify_phone_code(*, phone: str, code: Optional[str], last4: Optional[str]) -> VerifyResult:
    now = timezone.now()

    if code:
        method = PhoneVerificationCode.Method.SMS
        qs = PhoneVerificationCode.objects.select_for_update().filter(
            phone_e164=phone, method=method, used=False, expires_at__gt=now
        )
    else:
        method = PhoneVerificationCode.Method.CALL
        qs = PhoneVerificationCode.objects.select_for_update().filter(
            phone_e164=phone, method=method, used=False, expires_at__gt=now
        )

    rec = qs.order_by("-created_at").first()
    if not rec:
        return VerifyResult(ok=False, reason="not_found_or_expired", user_payload=None)

    if rec.attempts >= MAX_ATTEMPTS:
        return VerifyResult(ok=False, reason="too_many_attempts", user_payload=None)

    ok = False
    if method == PhoneVerificationCode.Method.SMS:
        ok = (code == rec.code)
    else:
        ok = (last4 == rec.last4_expected)

    if not ok:
        rec.attempts += 1
        rec.save(update_fields=["attempts"])
        return VerifyResult(ok=False, reason="wrong_code", user_payload=None)

    # success
    rec.used = True
    rec.used_at = now
    rec.save(update_fields=["used", "used_at"])

    # dev "user"
    payload = {
        "id": rec.id,  # временно id = id записи для простоты
        "phone": phone,
        "role": "user",
    }
    return VerifyResult(ok=True, reason=None, user_payload=payload)

def _mask_email(email: str) -> str:
    try:
        user, dom = email.split("@", 1)
    except ValueError:
        return email
    um = (user[:1] or "*") + "***"
    dm = (dom[:1] or "*") + "***"
    return f"{um}@{dm}"

@dataclass
class IssueEmailResult:
    record: EmailVerificationCode
    created: bool

def _generate_email_code() -> str:
    return f"{random.randint(0, 999999):06d}"

def issue_email_code(*, email: str, ip: Optional[str], ua: Optional[str]) -> IssueEmailResult:
    now = timezone.now()
    expires_at = now + timezone.timedelta(minutes=TTL_MINUTES)
    # reuse active
    existing = (
        EmailVerificationCode.objects.filter(email=email, used=False, expires_at__gt=now)
        .order_by("-created_at")
        .first()
    )
    if existing:
        rec = existing
        created = False
    else:
        rec = EmailVerificationCode(
            email=email,
            code=_generate_email_code(),
            expires_at=expires_at,
            ip=ip or "",
            ua=(ua or "")[:256],
        )
        rec.save()
        created = True

    # send via Django email backend (Mailhog in dev)
    subject = "Layba: ваш код подтверждения"
    body = f"Ваш код: {rec.code} (действует 10 минут)."
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@layba.local"),
        to=[email],
    )
    try:
        msg.send(fail_silently=True)
    finally:
        logger_email.info("email code sent to %s", _mask_email(email))

    return IssueEmailResult(record=rec, created=created)

@dataclass
class ConfirmEmailResult:
    ok: bool
    reason: Optional[str]
    user_payload: Optional[dict]

@transaction.atomic
def confirm_email_code(*, email: str, code: str) -> ConfirmEmailResult:
    now = timezone.now()
    rec = (
        EmailVerificationCode.objects.select_for_update()
        .filter(email=email, used=False, expires_at__gt=now)
        .order_by("-created_at")
        .first()
    )
    if not rec:
        return ConfirmEmailResult(ok=False, reason="not_found_or_expired", user_payload=None)

    if rec.attempts >= MAX_ATTEMPTS:
        return ConfirmEmailResult(ok=False, reason="too_many_attempts", user_payload=None)

    if rec.code != code:
        rec.attempts += 1
        rec.save(update_fields=["attempts"])
        return ConfirmEmailResult(ok=False, reason="wrong_code", user_payload=None)

    rec.used = True
    rec.used_at = now
    rec.save(update_fields=["used", "used_at"])

    payload = {"id": rec.id, "email": rec.email, "role": "user"}
    return ConfirmEmailResult(ok=True, reason=None, user_payload=payload)