import os
from datetime import timedelta
from pathlib import Path

import environ
from firebase_admin import initialize_app


BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))


DEBUG = env.bool("IS_DEBUG", default=False)
print("DEBUG", DEBUG)

SECRET_KEY = env("DJANGO_SECRET_KEY")
print("SECRET_KEY", SECRET_KEY)
DB_ENGINE=env("DB_ENGINE", cast=str)
print("DB_ENGINE", DB_ENGINE)
DB_NAME=env("DB_NAME")
print("DB_NAME", DB_NAME)
DB_USER=env("DB_USER")
print("DB_USER", DB_USER)
DB_PASSWORD=env("DB_PASSWORD")
print("DB_PASSWORD", DB_PASSWORD)
DB_HOST=env("DB_HOST")
print("DB_HOST", DB_HOST)
DB_PORT=env("DB_PORT")
print("DB_PORT", DB_PORT)

DATABASES = {
    "default": {
        "ENGINE": DB_ENGINE,
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "ATOMIC_REQUESTS": True,
    }
}

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "django_filters",
    "rest_framework.authtoken",
    "corsheaders",
    "fcm_django",
    # Original apps
    "accounts",
    "campuses",
    "comments",
    "items",
    "notifications",
    "terms_and_conditions",
    "transaction_messages",
    'storages',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
# ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
print("ALLOWED_HOSTS", ALLOWED_HOSTS)

# STATIC_URL = "static/"
# STATIC_ROOT = env("STATIC_ROOT", default=os.path.join(BASE_DIR, "static"))

# MEDIA_URL = "media/"
# MEDIA_ROOT = env("MEDIA_ROOT", default=os.path.join(BASE_DIR, "media"))

STATIC_ROOT="./static"
MEDIA_ROOT="./media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    # "DEFAULT_AUTHENTICATION_CLASSES": [
    #     "accounts.authentication.CookieJWTAuthentication",
    # ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.firebase_auth.FirebaseAuthentication",
    ],
    "DEFAULT_MAX_FILE_SIZE": 10 * 1024 * 1024,  # 最大ファイルサイズ (10MB)
}

CORS_ALLOW_ALL_ORIGINS = True
# CLIENT_URL = env("CLIENT_URL")
# if DEBUG:
#       # どのリクエストでも許可
# else:
#     CORS_ORIGIN_WHITELIST = [CLIENT_URL]  # ホワイトリストに設定したCLIENT_URL（今回はNode.js）のみリクエストを許可
#     CORS_ALLOWED_ORIGINS = [CLIENT_URL]
# # CSRFトークンの設定
# CSRF_TRUSTED_ORIGINS = [CLIENT_URL]


SIMPLE_JWT = {
    # アクセストークン(1時間)
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    # リフレッシュトークン(3日)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=3),
    # 認証タイプ
    "AUTH_HEADER_TYPES": ("JWT",),
    # 認証トークン
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# CLIENT_SITE_NAME = env("CLIENT_SITE_NAME")

# FCM関連
FIREBASE_APP = initialize_app()

# --- GCPの設定
import os
from google.oauth2 import service_account

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

GS_BUCKET_NAME = 'uniboo-strage'

STATIC_URL = '/static/'

# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = env("MEDIA_URL")


# ローカル用
# GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
#     os.path.join(BASE_DIR, 'mnt/storage-secret/storage-key')
# )

# # 本番用
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    '/mnt/storage-secret/storage-key'
)
print("GS_CREDENTIALS", GS_CREDENTIALS)
