import uuid
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.throttling import ScopedRateThrottle
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .serializers import (
    PhoneSendCodeIn, PhoneVerifyIn,
    EmailSendCodeIn, EmailConfirmIn,
    SessionLoginIn,
    SocialGoogleIn, SocialFacebookIn, SocialAppleIn, ErrorSerializer,
)

def _err(code:str, message:str, details:dict|None=None, http_status:int=400):
    return Response({
        "code": code,
        "message": message,
        "details": details or {},
        "request_id": str(uuid.uuid4()),
    }, status=http_status)

def _ok(data:dict|None=None, http_status:int=200):
    return Response(data or {"ok": True}, status=http_status)

class HasSession(BasePermission):
    def has_permission(self, request, view):
        return bool(request.session.get("user"))

@method_decorator(ensure_csrf_cookie, name="dispatch")
@extend_schema(
    operation_id="auth_csrf",
    description="Issue CSRF cookie (dev)",
    responses={200: OpenApiTypes.OBJECT},
)
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
            return _err("validation_error", "Invalid payload", ser.errors, 400)
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

class CsrfViewDeprecated(CsrfView):
    pass

@extend_schema(
    responses={
        200: OpenApiResponse(description="Current session profile"),
        401: ErrorSerializer,
    }
)
class ProfileMeView(APIView):
     authentication_classes: list = []
     permission_classes: list = []
     def get(self, request):
         user = request.session.get("user")
         if not user:
             return _err("unauthorized", "Authentication required", {}, 401)
         return _ok(user, 200)

class PhoneSendCodeView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "phone_send_code"

    @extend_schema(
        responses={204: OpenApiResponse(description="Code sent"), 400: ErrorSerializer, 429: ErrorSerializer})
    def post(self, request):
        ser = PhoneSendCodeIn(data=request.data)
        if not ser.is_valid():
            return _err("validation_error", "Invalid payload", ser.errors, 400)
        # dev stub: do nothing, pretend sent
        return _ok({}, status.HTTP_204_NO_CONTENT)

class PhoneVerifyView(APIView):
    @extend_schema(responses={200: OpenApiResponse(description="Authorized"), 400: ErrorSerializer})
    def post(self, request):
        ser = PhoneVerifyIn(data=request.data)
        if not ser.is_valid():
            return _err("validation_error", "Invalid payload", ser.errors, 400)
        # dev stub: authenticate test user and "log in"
        request.session["user"] = {"id": 1, "email": "phone-user@example.com", "role": "user"}
        request.session.save()
        return _ok(request.session["user"], 200)

class EmailSendCodeView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "email_send_code"

    @extend_schema(
        responses={204: OpenApiResponse(description="Email sent"), 400: ErrorSerializer, 429: ErrorSerializer})
    def post(self, request):
        ser = EmailSendCodeIn(data=request.data)
        if not ser.is_valid():
            return _err("validation_error", "Invalid payload", ser.errors, 400)
        # dev stub: in dev it "goes" to Mailhog
        return _ok({}, status.HTTP_204_NO_CONTENT)

class EmailConfirmView(APIView):
    @extend_schema(responses={200: OpenApiResponse(description="Email confirmed"), 400: ErrorSerializer})
    def post(self, request):
        ser = EmailConfirmIn(data=request.data)
        if not ser.is_valid():
            return _err("validation_error", "Invalid payload", ser.errors, 400)
        # dev stub: mark as confirmed (no-op)
        return _ok({"email_confirmed": True}, 200)

class SocialGoogleView(APIView):
    @extend_schema(responses={200: OpenApiResponse(description="Google profile"), 400: ErrorSerializer})
    def post(self, request):
        ser = SocialGoogleIn(data=request.data)
        if not ser.is_valid():
            return _err("validation_error", "Invalid payload", ser.errors, 400)
        return _ok({"provider": "google", "profile": {"email": "user@example.com"}}, 200)

class SocialFacebookView(APIView):
    @extend_schema(responses={200: OpenApiResponse(description="Facebook profile"), 400: ErrorSerializer})
    def post(self, request):
        ser = SocialFacebookIn(data=request.data)
        if not ser.is_valid():
            return _err("validation_error", "Invalid payload", ser.errors, 400)
        return _ok({"provider": "facebook", "profile": {"email": "user@example.com"}}, 200)

class SocialAppleView(APIView):
    @extend_schema(responses={200: OpenApiResponse(description="Apple profile"), 400: ErrorSerializer})
    def post(self, request):
        ser = SocialAppleIn(data=request.data)
        if not ser.is_valid():
            return _err("validation_error", "Invalid payload", ser.errors, 400)
        return _ok({"provider": "apple", "profile": {"email": "user@example.com"}}, 200)

@extend_schema(responses={200: OpenApiResponse(description="Moderator settings"), 401: ErrorSerializer, 403: ErrorSerializer})
class ModeratorNotificationSettingsView(APIView):
    def get(self, request):
        user = request.session.get("user")
        if not user:
            return _err("unauthorized", "Authentication required", {}, 401)
        if user.get("role") != "moderator":
            return _err("forbidden", "Moderator role required", {}, 403)
        # dev stub
        return _ok({"email": True, "sms": False}, 200)

    @extend_schema(responses={200: OpenApiResponse(description="Saved"), 401: ErrorSerializer, 403: ErrorSerializer})
    def put(self, request):
        user = request.session.get("user")
        if not user:
            return _err("unauthorized", "Authentication required", {}, 401)
        if user.get("role") != "moderator":
            return _err("forbidden", "Moderator role required", {}, 403)
        # dev stub: echo back
        return _ok(request.data or {"email": True, "sms": False}, 200)
