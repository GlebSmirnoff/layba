from django.db import models
from django.utils import timezone


class PhoneVerificationCode(models.Model):
    class Method(models.TextChoices):
        SMS = "sms", "SMS"
        CALL = "call", "CALL"

    phone_e164 = models.CharField(max_length=20, db_index=True)
    method = models.CharField(max_length=8, choices=Method.choices, db_index=True)
    code = models.CharField(max_length=6, null=True, blank=True)
    last4_expected = models.CharField(max_length=4, null=True, blank=True)
    expires_at = models.DateTimeField(db_index=True)
    used = models.BooleanField(default=False, db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    ip = models.GenericIPAddressField(null=True, blank=True)
    ua = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["phone_e164", "used", "created_at"]),
        ]
        ordering = ["-created_at"]

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def __str__(self) -> str:
        return f"{self.phone_e164} [{self.method}] used={self.used}"

