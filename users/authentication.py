from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that checks if the token's issued at (iat) time
    is before the user's last logout time.
    """

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if user and user.last_logout:
            iat = validated_token.get('iat')
            if iat:
                from datetime import datetime
                token_iat = datetime.fromtimestamp(
                    iat, tz=user.last_logout.tzinfo
                )
                if token_iat < user.last_logout:
                    raise AuthenticationFailed(
                        "This token is invalid because the user has logged out.", # noqa
                        code='token_not_valid'
                    )
        return user
