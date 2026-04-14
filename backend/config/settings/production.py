from __future__ import annotations

import os

from .base import *  # noqa: F401, F403

DEBUG = False

if not SECRET_KEY:  # noqa: F405
    raise ValueError("DJANGO_SECRET_KEY environment variable is required in production")

_hosts_str = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _hosts_str.split(",") if h.strip()]
if not ALLOWED_HOSTS:
    raise ValueError("DJANGO_ALLOWED_HOSTS environment variable is required in production")

_cors_str = os.environ.get("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_str.split(",") if o.strip()]

SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "True").lower() == "true"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Кэш: Redis общий для всех gunicorn-воркеров.
# Нужен, чтобы django-ratelimit корректно считал лимиты по IP в многопроцессной среде.
# Если REDIS_URL не задан — падаем на LocMemCache (ratelimit будет считать per-worker).
_REDIS_URL = os.environ.get("REDIS_URL", "")
if _REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": _REDIS_URL,
        }
    }

