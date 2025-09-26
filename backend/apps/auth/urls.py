from django.urls import path
from .views import (
    CsrfView,
    SessionLoginView, SessionLogoutView,
    PhoneSendCodeView, PhoneVerifyView,
    EmailSendCodeView, EmailConfirmView,
    SocialGoogleView, SocialFacebookView, SocialAppleView,
    ModeratorNotificationSettingsView,
)

urlpatterns = [
    # Web sessions
    path("session/login", SessionLoginView.as_view(), name="auth-session-login"),
    path("session/logout", SessionLogoutView.as_view(), name="auth-session-logout"),
    path("csrf/", CsrfView.as_view(), name="auth-csrf"),  # dev helper

    # Phone
    path("phone/send_code", PhoneSendCodeView.as_view(), name="auth-phone-send"),
    path("phone/verify", PhoneVerifyView.as_view(), name="auth-phone-verify"),

    # Email
    path("email/send_code", EmailSendCodeView.as_view(), name="auth-email-send"),
    path("email/confirm", EmailConfirmView.as_view(), name="auth-email-confirm"),

    # OAuth2
    path("social/google", SocialGoogleView.as_view(), name="auth-social-google"),
    path("social/facebook", SocialFacebookView.as_view(), name="auth-social-facebook"),
    path("social/apple", SocialAppleView.as_view(), name="auth-social-apple"),
]
