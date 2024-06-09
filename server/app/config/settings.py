import os
import sys
from datetime import timedelta
from pathlib import Path

import environ
from firebase_admin import initialize_app

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = env.bool("IS_DEBUG", default=False)

SECRET_KEY = env("DJANGO_SECRET_KEY")

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
    "djoser",
    "corsheaders",
    "fcm_django",
    "anymail",
    # Original apps
    "accounts",
    "campuses",
    "comments",
    "items",
    "notifications",
    "terms_and_conditions",
    "transaction_messages",
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

DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE"),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
        "ATOMIC_REQUESTS": True,
    }
}

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

STATIC_URL = "static/"
STATIC_ROOT = env("STATIC_ROOT", default=os.path.join(BASE_DIR, "static"))

MEDIA_URL = "media/"
MEDIA_ROOT = env("MEDIA_ROOT", default=os.path.join(BASE_DIR, "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CookieJWTAuthentication",
    ],
    "DEFAULT_MAX_FILE_SIZE": 10 * 1024 * 1024,  # 最大ファイルサイズ (10MB)
}

CLIENT_URL = env("CLIENT_URL")
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True  # どのリクエストでも許可
    CORS_ALLOW_CREDENTIALS = True  # Cookieの送信の許可
else:
    CORS_ORIGIN_WHITELIST = [CLIENT_URL]  # ホワイトリストに設定したCLIENT_URL（今回はNode.js）のみリクエストを許可
    CORS_ALLOWED_ORIGINS = [CLIENT_URL]
# CSRFトークンの設定
CSRF_TRUSTED_ORIGINS = [CLIENT_URL]

# CORS(クロスドメインリクエスト)でCookieを送信することを許可
CORS_ALLOW_CREDENTIALS = True
# HTTPSの設定とクロスドメインの許可設定
if DEBUG:
    SESSION_COOKIE_SECURE = False
else:
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True

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

# メールサーバー
EMAIL_BACKEND = env("EMAIL_BACKEND")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=None)
ANYMAIL = {
    "MAILGUN_API_KEY": env("MAILGUN_API_KEY", default=None),
    "MAILGUN_SENDER_DOMAIN": env("MAILGUN_SENDER_DOMAIN", default=None),
}
SERVER_EMAIL = env("SERVER_EMAIL", default=None)

DJOSER = {
    # メールアドレスでログイン
    "LOGIN_FIELD": "email",
    # アカウント本登録メール
    "SEND_ACTIVATION_EMAIL": True,
    # アカウント本登録完了メール
    "SEND_CONFIRMATION_EMAIL": True,
    # メールアドレス変更完了メール
    "USERNAME_CHANGED_EMAIL_CONFIRMATION": True,
    # パスワード変更完了メール
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    # アカウント登録時に確認用パスワード必須
    "USER_CREATE_PASSWORD_RETYPE": True,
    # メールアドレス変更時に確認用メールアドレス必須
    "SET_USERNAME_RETYPE": True,
    # パスワード変更時に確認用パスワード必須
    "SET_PASSWORD_RETYPE": True,
    # アカウント本登録用URL
    "ACTIVATION_URL": "uniboo://auth/?uid={uid}&token={token}",
    # メールアドレスリセット完了用URL
    "USERNAME_RESET_CONFIRM_URL": "email/reset/confirm/{uid}/{token}/",
    # パスワードリセット完了用URL
    "PASSWORD_RESET_CONFIRM_URL": "password/reset/confirm/{uid}/{token}/",
    # カスタムユーザー用シリアライザー
    "SERIALIZERS": {
        "user_create": "accounts.serializers.UserSerializer",
        "user_create_password_retype": "accounts.serializers.UserCreateSerializer",
        "user": "accounts.serializers.UserSerializer",
        "current_user": "accounts.serializers.UserSerializer",
        "user_delete": "accounts.serializers.UserDeleteSerializer",
    },
    "PERMISSIONS": {
        "user": ["djoser.permissions.CurrentUserOrAdminOrReadOnly"],
    },
    "EMAIL": {
        # アカウント本登録
        "activation": "accounts.email.ActivationEmail",
        # アカウント本登録完了
        "confirmation": "accounts.email.ConfirmationEmail",
    },
}

CLIENT_SITE_NAME = env("CLIENT_SITE_NAME")

# FCM関連
FIREBASE_APP = initialize_app()

# debug_toolbar
ENABLE_DEBUG_TOOLBAR = DEBUG and "test" not in sys.argv
if ENABLE_DEBUG_TOOLBAR:
    def show_toolbar(request):
        # すべてのリクエストに対してデバッグツールバーを表示
        return True
    
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    }
