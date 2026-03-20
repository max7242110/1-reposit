from .base import *  # noqa: F401, F403

DEBUG = True

SECRET_KEY = "django-insecure-dev-key-do-not-use-in-production"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"] = None  # type: ignore[name-defined]  # noqa: F405
