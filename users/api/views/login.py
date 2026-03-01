import logging
from rest_framework import generics, permissions, status, serializers
from rest_framework.throttling import ScopedRateThrottle
from django.utils import timezone
from users.api.serializers import (
    UserSerializer,
    LoginSerializer,
)
from core.utils.response import CustomResponse
from core.utils.exceptions import custom_exception_handler
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger('user')


class LoginView(generics.GenericAPIView):
    """
    User login view returning JWT tokens.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']

            # Update last login timestamp
            user.last_login = timezone.now()
            user.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            logger.info(f"User {user.email} logged in successfully.")

            data = {
                'user': UserSerializer(
                    user, context={'request': request}
                ).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return CustomResponse.success(
                message='Login successful',
                data=data,
                status_code=status.HTTP_200_OK
            )

        except serializers.ValidationError as e:
            logger.error(f"Failed to login: {str(e)}")
            return custom_exception_handler(e, request)

        except Exception as e:
            logger.error(f"Failed to login: {str(e)}")
            return custom_exception_handler(e, request)
