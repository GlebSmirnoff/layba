import uuid
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.throttling import ScopedRateThrottle
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    PhoneSendCodeIn, PhoneVerifyIn,
    EmailSendCodeIn, EmailConfirmIn,
    SessionLoginIn, ErrorSerializer,
    SocialGoogleIn, SocialFacebookIn, SocialAppleIn
)
from .services import issue_phone_code, verify_phone_code
from .models import PhoneVerificationCode

def _error(code: str, message: str, details=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": "",  # можно подшить request-id мидлварью на шаге 7
        },
        status=status_code,
    )

def _ok(data:dict|None=None, http_status:int=200):
    return Response(data or {"ok": True}, status=http_status)

class HasSession(BasePermission):
    def has_permission(self, request, view):
        return bool(request.session.get("user"))

@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        # Force CSRF token generation and set cookie
        token = get_token(request)
        return _ok({"csrf": token})

class SessionLoginView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        ser = SessionLoginIn(data=request.data)
        if not ser.is_valid():
            return _error("validation_error", "Invalid payload", ser.errors, 400)
        data = ser.validated_data
        email = data.get("email") or "user@example.com"
        role = data.get("role") or "user"
        # dev stub: set session
        request.session["user"] = {"id": 1, "email": email, "role": role}
        request.session.save()
        return _ok(request.session["user"], 200)

class SessionLogoutView(APIView):
    def post(self, request):
        request.session.flush()
        return _ok({}, status.HTTP_204_NO_CONTENT)

class ProfileMeView(APIView):
    permission_classes = [HasSession]

    def get(self, request):
        user = request.session.get("user")
        if not user:
            return _error("unauthorized", "Authentication required", {}, 401)
        return _ok(user, 200)

class PhoneSendCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "phone_send_code"

    @extend_schema(
        request=PhoneSendCodeIn,
        responses={
            204: OpenApiResponse(description="No Content"),
            400: ErrorSerializer,
            429: ErrorSerializer,
        },
    )
    def post(self, request):
        serializer = PhoneSendCodeIn(data=request.data)
        if not serializer.is_valid():
            return _error("validation_error", "Invalid payload", serializer.errors, status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        ip = request.META.get("REMOTE_ADDR")
        ua = request.META.get("HTTP_USER_AGENT")
        try:
            issue_phone_code(phone=data["phone"], method=data["method"], ip=ip, ua=ua)
        except ValueError as e:
            return _error("validation_error", str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

class PhoneVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "phone_verify"

    @extend_schema(
        request=PhoneVerifyIn,
        responses={
            200: OpenApiResponse(description="OK"),
            400: ErrorSerializer,
            401: ErrorSerializer,
            410: ErrorSerializer,
            429: ErrorSerializer,
        },
    )
    def post(self, request):
        s = PhoneVerifyIn(data=request.data)
        if not s.is_valid():
            return _error("validation_error", "Invalid payload", s.errors, status.HTTP_400_BAD_REQUEST)
        v = s.validated_data
        res = verify_phone_code(phone=v["phone"], code=v.get("code"), last4=v.get("last4"))
        if not res.ok:
            if res.reason == "not_found_or_expired":
                return _error("gone", "Code expired or not found", status_code=status.HTTP_410_GONE)
            if res.reason == "too_many_attempts":
                return _error("too_many_attempts", "Too many attempts", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
            return _error("unauthorized", "Wrong code", status_code=status.HTTP_401_UNAUTHORIZED)

        # web-сессия
        request.session["user"] = {"id": res.user_payload["id"], "email": "phone-user@example.com", "role": "user"}
        request.session.save()
        return Response(res.user_payload, status=status.HTTP_200_OK)

class EmailSendCodeView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "email_send_code"

    def post(self, request):
        ser = EmailSendCodeIn(data=request.data)
        if not ser.is_valid():
            return _error("validation_error", "Invalid payload", ser.errors, 400)
        # dev stub: in dev it "goes" to Mailhog
        return _ok({}, status.HTTP_204_NO_CONTENT)

class EmailConfirmView(APIView):
    def post(self, request):
        ser = EmailConfirmIn(data=request.data)
        if not ser.is_valid():
            return _error("validation_error", "Invalid payload", ser.errors, 400)
        # dev stub: mark as confirmed (no-op)
        return _ok({"email_confirmed": True}, 200)

class SocialGoogleView(APIView):
    def post(self, request):
        ser = SocialGoogleIn(data=request.data)
        if not ser.is_valid():
            return _error("validation_error", "Invalid payload", ser.errors, 400)
        return _ok({"provider": "google", "profile": {"email": "user@example.com"}}, 200)

class SocialFacebookView(APIView):
    def post(self, request):
        ser = SocialFacebookIn(data=request.data)
        if not ser.is_valid():
            return _error("validation_error", "Invalid payload", ser.errors, 400)
        return _ok({"provider": "facebook", "profile": {"email": "user@example.com"}}, 200)

class SocialAppleView(APIView):
    def post(self, request):
        ser = SocialAppleIn(data=request.data)
        if not ser.is_valid():
            return _error("validation_error", "Invalid payload", ser.errors, 400)
        return _ok({"provider": "apple", "profile": {"email": "user@example.com"}}, 200)

class ModeratorNotificationSettingsView(APIView):
    def get(self, request):
        user = request.session.get("user")
        if not user:
            return _error("unauthorized", "Authentication required", {}, 401)
        if user.get("role") != "moderator":
            return _error("forbidden", "Moderator role required", {}, 403)
        # dev stub
        return _ok({"email": True, "sms": False}, 200)

    def put(self, request):
        user = request.session.get("user")
        if not user:
            return _error("unauthorized", "Authentication required", {}, 401)
        if user.get("role") != "moderator":
            return _error("forbidden", "Moderator role required", {}, 403)
        # dev stub: echo back
        return _ok(request.data or {"email": True, "sms": False}, 200)
