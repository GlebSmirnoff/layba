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
    PhoneSendCodeIn,
    PhoneVerifyIn,
    EmailSendCodeIn,
    EmailConfirmIn,
    SessionLoginIn,
    SocialGoogleIn,
    SocialFacebookIn,
    SocialAppleIn,
    ErrorSerializer,
)
from .services import (
    issue_phone_code,
    verify_phone_code,
    issue_email_code,
    confirm_email_code,
)


# ---------- helpers ----------
def _error(code: str, message: str, details=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": "",
        },
        status=status_code,
    )


def _set_session_user(request, user_dict: dict):
    request.session["user"] = user_dict


class IsAuthenticatedSession(BasePermission):
    def has_permission(self, request, view):
        return bool(request.session.get("user"))


# ---------- CSRF ----------
@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes: list = []

    @extend_schema(
        responses={200: OpenApiResponse(description="Set CSRF cookie and return token")},
    )
    def get(self, request):
        token = get_token(request)
        return Response({"csrf": token})


# ---------- PROFILE ----------
class ProfileMeView(APIView):
    permission_classes = [IsAuthenticatedSession]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Authenticated profile"),
            403: ErrorSerializer,
        }
    )
    def get(self, request):
        user = request.session.get("user")
        if not user:
            return _error("forbidden", "Authentication required", status_code=status.HTTP_403_FORBIDDEN)
        return Response(user)


# ---------- SESSION (demo) ----------
class SessionLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=SessionLoginIn)
    def post(self, request):
        s = SessionLoginIn(data=request.data)
        if not s.is_valid():
            return _error("validation_error", "Invalid payload", s.errors, status.HTTP_400_BAD_REQUEST)

        data = s.validated_data
        user = {
            "id": 1,
            "email": data.get("email") or "user@example.com",
            "role": data.get("role") or "user",
        }
        _set_session_user(request, user)
        return Response(user)


class SessionLogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        request.session.flush()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- PHONE ----------
class PhoneSendCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "phone_send_code"

    @extend_schema(request=PhoneSendCodeIn, responses={204: OpenApiResponse(description="Code issued")})
    def post(self, request):
        s = PhoneSendCodeIn(data=request.data)
        if not s.is_valid():
            return _error("validation_error", "Invalid payload", s.errors, status.HTTP_400_BAD_REQUEST)

        data = s.validated_data
        issue_phone_code(
            phone=data["phone"],
            method=data.get("method") or "sms",
            ip=request.META.get("REMOTE_ADDR"),
            ua=request.META.get("HTTP_USER_AGENT"),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PhoneVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "phone_verify"

    @extend_schema(request=PhoneVerifyIn, responses={200: OpenApiResponse(description="Authenticated")})
    def post(self, request):
        s = PhoneVerifyIn(data=request.data)
        if not s.is_valid():
            return _error("validation_error", "Invalid payload", s.errors, status.HTTP_400_BAD_REQUEST)

        data = s.validated_data
        try:
            user, _rec = verify_phone_code(
                phone=data["phone"],
                code=data.get("code"),
                last4=data.get("last4"),
            )
        except ValueError as e:  # "gone"
            return _error("gone", "Code expired or not found", status_code=status.HTTP_410_GONE)
        except PermissionError as e:
            msg = str(e)
            if msg == "too_many_attempts":
                return _error("too_many_attempts", "Too many attempts", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
            return _error("unauthorized", "Invalid code", status_code=status.HTTP_401_UNAUTHORIZED)

        _set_session_user(request, user)
        return Response(user)


# ---------- EMAIL ----------
class EmailSendCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "email_send_code"

    @extend_schema(request=EmailSendCodeIn, responses={204: OpenApiResponse(description="Code issued")})
    def post(self, request):
        s = EmailSendCodeIn(data=request.data)
        if not s.is_valid():
            return _error("validation_error", "Invalid payload", s.errors, status.HTTP_400_BAD_REQUEST)

        data = s.validated_data
        issue_email_code(
            email=data["email"],
            ip=request.META.get("REMOTE_ADDR"),
            ua=request.META.get("HTTP_USER_AGENT"),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "email_confirm"

    @extend_schema(request=EmailConfirmIn, responses={200: OpenApiResponse(description="Authenticated")})
    def post(self, request):
        s = EmailConfirmIn(data=request.data)
        if not s.is_valid():
            return _error("validation_error", "Invalid payload", s.errors, status.HTTP_400_BAD_REQUEST)

        data = s.validated_data
        try:
            user, _rec = confirm_email_code(
                email=data["email"],
                code=data["code"],
            )
        except ValueError:
            return _error("gone", "Code expired or not found", status_code=status.HTTP_410_GONE)
        except PermissionError as e:
            msg = str(e)
            if msg == "too_many_attempts":
                return _error("too_many_attempts", "Too many attempts", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
            return _error("unauthorized", "Invalid code", status_code=status.HTTP_401_UNAUTHORIZED)

        _set_session_user(request, user)
        return Response(user)
