from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.auth.views import (
    ProfileMeView,
    CsrfView,
    CsrfViewDeprecated,  # NEW
    ModeratorNotificationSettingsView,)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("health.urls")),
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

# Auth bundle
    path("auth/", include("apps.auth.urls")),
    path("auth/csrf/", CsrfView.as_view(), name="auth-csrf"),                 # NEW: основной путь
    path("csrf/", CsrfViewDeprecated.as_view(), name="csrf-deprecated"),      # NEW: алиас (deprecated)
    path("profile/me", ProfileMeView.as_view(), name="profile-me"),
    path("api/notifications/settings/", ModeratorNotificationSettingsView.as_view(),
         name="moderator-notifications-settings"),

]

