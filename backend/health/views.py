from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
import os, redis

def healthz(request):
    return JsonResponse({"status": "ok", "service": "backend"})

def readiness(request):
    checks = {}

    # DB
    try:
        connections["default"].cursor()
        checks["db"] = "ok"
    except OperationalError as e:
        checks["db"] = f"error: {e}"

    # Redis (по желанию; у нас есть REDIS_URL в .env)
    try:
        r = redis.StrictRedis.from_url(os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"))
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    status = 200 if all(v == "ok" for v in checks.values()) else 503
    return JsonResponse({"status": "ready" if status == 200 else "degraded", "checks": checks}, status=status)

