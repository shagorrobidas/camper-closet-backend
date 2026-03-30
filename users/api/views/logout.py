from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.utils import datetime_from_epoch
from users.api.serializers import LogoutSerializer
from core.utils import CustomResponse
from django.utils import timezone


class LogoutView(APIView):
    """
    User logout view that blacklists the refresh token.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data['refresh']

        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Manual Blacklist Access Token in Database
            access_token = request.auth
            auth_header = request.headers.get('Authorization', '')
            if access_token and auth_header.startswith('Bearer '):
                try:
                    raw_token = auth_header.split(' ')[1]
                    outstanding_token, _ = OutstandingToken.objects.get_or_create(
                        jti=access_token.get('jti'),
                        defaults={
                            'token': raw_token,
                            'user': request.user,
                            'created_at': datetime_from_epoch(access_token.get('iat')),
                            'expires_at': datetime_from_epoch(access_token.get('exp')),
                        }
                    )
                    BlacklistedToken.objects.get_or_create(token=outstanding_token)
                except Exception:
                    pass

            # Update last_logout to invalidate current access tokens
            request.user.last_logout = timezone.now()
            request.user.save(update_fields=['last_logout'])

            return CustomResponse.success(
                message="Successfully logged out",
                status_code=status.HTTP_200_OK
            )
        except TokenError:
            return CustomResponse.error(
                message="Token is invalid or expired.",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
