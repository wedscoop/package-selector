import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_URL = '/static/'
SECRET_KEY = "dev-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# -------------------------
# APPS
# -------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

# -------------------------
# MIDDLEWARE
# -------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# -------------------------
# URLS
# -------------------------
ROOT_URLCONF = "project.urls"

# -------------------------
# TEMPLATES
# -------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -------------------------
# WSGI
# -------------------------
WSGI_APPLICATION = "project.wsgi.application"

# -------------------------
# DATABASE (SQLite)
# -------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------
# STATIC FILES
# -------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# -------------------------
# DEFAULT PK FIELD (removes warning)
# -------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

print("STATIC DIR:", STATICFILES_DIRS)

ALLOWED_HOSTS = ["*"]  # temp, we’ll tighten later

DEBUG = False

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    ...
]