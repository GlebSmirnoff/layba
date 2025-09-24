from django.urls import path
from .views import healthz, readiness

urlpatterns = [
    path("healthz", healthz, name="healthz"),
    path("readiness", readiness, name="readiness"),
]
