from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES["default"]["HOST"] = os.getenv("DB_HOST", "localhost")

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5555",  # React padrão
]
# CORS_ALLOW_ALL_ORIGINS = True