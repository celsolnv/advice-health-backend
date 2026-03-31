
from .base import *

DEBUG = False

if not SECRET_KEY:
    raise ValueError("SECRET_KEY não definida no ambiente de produção.")

if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS não definida no ambiente de produção.")

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"