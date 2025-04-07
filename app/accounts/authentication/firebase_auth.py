from firebase_admin import auth as firebase_auth
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import firebase_admin
from firebase_admin import credentials

User = get_user_model()

class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Authorization ヘッダーからトークンを取得
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None  # 他の認証に委ねる

        id_token = auth_header.split("Bearer ")[1]
 
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            firebase_uid = decoded_token["uid"]
            firebase_email = decoded_token.get("email")
        except Exception as e:
            raise AuthenticationFailed(f"Firebase認証に失敗しました: {e}")

        # Firebaseのuidでユーザーを取得 or 作成
        try:
            user, created = User.objects.get_or_create(
                email=firebase_email,
                defaults={"is_active": True},
            )
            return (user, None)
        except Exception as e:
            raise AuthenticationFailed(f"ユーザーの取得または作成に失敗しました: {e}")
