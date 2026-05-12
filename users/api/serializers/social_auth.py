import logging
from django.conf import settings
from rest_framework import serializers
from users.models import User, AuthProvider
from users.api.serializers import UserSerializer
import firebase_admin
from firebase_admin import credentials, auth
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


def verify_firebase_token(id_token):
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_FILE)
        firebase_admin.initialize_app(cred)

    return auth.verify_id_token(id_token)


class FirebaseAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()

    def validate(self, attrs):
        id_token = attrs.get("id_token")
        
        logger.debug(f"Received Firebase token: {id_token[:50]}...")
        
        try:
            decoded = verify_firebase_token(id_token)
            logger.debug(f"Token decoded successfully: {decoded}")
        except Exception as e:
            logger.error(
                f"Firebase verification error: {type(e).__name__} - {str(e)}",
                exc_info=True
            )
            raise serializers.ValidationError({"firebase_error": str(e)})

        email = decoded.get("email")
        name = decoded.get("name", "")
        picture = decoded.get("picture")

        # Map Firebase provider to our AuthProvider choices
        firebase_data = decoded.get("firebase", {})
        sign_in_provider = firebase_data.get("sign_in_provider", "")
        
        provider_mapping = {
            "google.com": AuthProvider.GOOGLE,
            "apple.com": AuthProvider.APPLE,
        }
        auth_provider = provider_mapping.get(sign_in_provider, AuthProvider.GOOGLE)

        # Create or Get User
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": name or email.split('@')[0],
                "role": "parent",  # Default to parent for social auth
                "is_active": True,
                "is_superuser": False,
                "is_staff": False,
                "auth_provider": auth_provider,
                "is_email_verified": True,
                "firebase_uid": decoded.get("uid"),
            }
        )

        # Ensure all fields are up-to-date even for existing users
        needs_save = False
        
        if not user.is_email_verified:
            user.is_email_verified = True
            needs_save = True
            
        if user.auth_provider != auth_provider:
            user.auth_provider = auth_provider
            needs_save = True

        if not user.firebase_uid and decoded.get("uid"):
            user.firebase_uid = decoded.get("uid")
            needs_save = True
            
        if picture and not user.profile_pic_url:
            user.profile_pic_url = picture
            needs_save = True
            
        if needs_save:
            user.save()

        # Generate your internal JWT tokens (SimpleJWT example)
        
        refresh = RefreshToken.for_user(user)

        return {
            "user": UserSerializer(user, context=self.context).data,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        }