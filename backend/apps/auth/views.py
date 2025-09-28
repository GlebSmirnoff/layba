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
    GoogleLoginIn,
    FacebookLoginIn,
    AppleLoginIn,
    ErrorSerializer,
)
from .services import (
    issue_phone_code,
    verify_phone_code,
    issue_email_code,
    confirm_email_code,
    google_exchange_code, google_verify_id_token,
    facebook_verify_access_token, apple_verify_id_token,
    find_or_create_user_from_social, issue_session_for,
)


# ---------- helpers ----------
def _error(code: str, message: str, details=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"code": code, "message": message, "details": details or {}, "request_id": ""}, status=status_code)


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

# --- permissions ---
class IsModerator(BasePermission):
    def has_permission(self, request, view):
        user = request.session.get("user")
        return bool(user) and user.get("role") == "moderator"


# --- moderator notifications settings (stub) ---
class ModeratorNotificationSettingsView(APIView):
    """
    GET/PUT /api/notifications/settings/
    Доступ только модератору. Возвращаем/принимаем простой объект {email: bool, sms: bool}.
    Хранения пока нет — echo/stub как в шаге 1–2.
    """
    permission_classes = [IsModerator]

    @extend_schema(
        responses={200: OpenApiResponse(description="Current moderator notification settings")},
    )
    def get(self, request):
        # Статический stub (как договаривались раньше)
        return Response({"email": True, "sms": False})

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Updated moderator notification settings")},
    )
    def put(self, request):
        data = request.data or {}
        email = bool(data.get("email", True))
        sms = bool(data.get("sms", False))
        return Response({"email": email, "sms": sms})


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

class SocialGoogleView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "social_login"

    @extend_schema(
        request=GoogleLoginIn,
        responses={200: OpenApiResponse(description="OK"), 401: ErrorSerializer, 400: ErrorSerializer},
    )
    def post(self, request):
        ser = GoogleLoginIn(data=request.data)
        if not ser.is_valid():
            return _error("validation_error", "Invalid payload", ser.errors)

        code = ser.validated_data.get("code")
        id_token = ser.validated_data.get("id_token")
        redirect_uri = ser.validated_data.get("redirect_uri")
        code_verifier = ser.validated_data.get("code_verifier")

        try:
            if id_token:
                payload = google_verify_id_token(id_token)
            elif code:
                tokens = google_exchange_code(code, redirect_uri, code_verifier)
                payload = google_verify_id_token(tokens["id_token"])
            else:
                return _error("validation_error", "Either code or id_token must be provided")
        except NotImplementedError as e:
            return _error("not_implemented", str(e), status_code=status.HTTP_501_NOT_IMPLEMENTED)
        except Exception:
            return _error("unauthorized", "Invalid Google token", status_code=status.HTTP_401_UNAUTHORIZED)

        user = find_or_create_user_from_social(payload, "google")
        issue_session_for(request, user)
        return Response(user, status=status.HTTP_200_OK)

# --- FACEBOOK ---
class SocialFacebookView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "social_login"

    @extend_schema(
        request=FacebookLoginIn,
        responses={200: OpenApiResponse(description="OK"), 401: ErrorSerializer, 400: ErrorSerializer},
    )
    def post(self, request):
        ser = FacebookLoginIn(data=request.data)
        if not ser.is_valid():
            return _error("validation_error", "Invalid payload", ser.errors)
        try:
            payload = facebook_verify_access_token(ser.validated_data["access_token"])
        except NotImplementedError as e:
            return _error("not_implemented", str(e), status_code=status.HTTP_501_NOT_IMPLEMENTED)
        except Exception:
            return _error("unauthorized", "Invalid Facebook token", status_code=status.HTTP_401_UNAUTHORIZED)

        user = find_or_create_user_from_social(payload, "facebook")
        issue_session_for(request, user)
        return Response(user, status=status.HTTP_200_OK)

# --- APPLE ---
class SocialAppleView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "social_login"

    @extend_schema(
        request=AppleLoginIn,
        responses={200: OpenApiResponse(description="OK"), 401: ErrorSerializer, 400: ErrorSerializer},
    )
    def post(self, request):
        ser = AppleLoginIn(data=request.data)
        if not ser.is_valid():
            return _error("validation_error", "Invalid payload", ser.errors)
        try:
            payload = apple_verify_id_token(ser.validated_data["id_token"])
        except NotImplementedError as e:
            return _error("not_implemented", str(e), status_code=status.HTTP_501_NOT_IMPLEMENTED)
        except Exception:
            return _error("unauthorized", "Invalid Apple token", status_code=status.HTTP_401_UNAUTHORIZED)

        user = find_or_create_user_from_social(payload, "apple")
        issue_session_for(request, user)
        return Response(user, status=status.HTTP_200_OK)