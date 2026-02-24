from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from users.api.serializers import (
    UserSerializer,
    OTPVerificationSerializer,
)
from users.utils import verify_otp
from users.tasks import send_welcome_email
from core.utils.response import CustomResponse
from core.utils.exceptions import custom_exception_handler
import logging

logger = logging.getLogger(__name__)


class VerifyOTPView(generics.GenericAPIView):
    """
    View to verify an OTP for various purposes.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = OTPVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp']
        purpose = serializer.validated_data['purpose']

        try:
            user = User.objects.get(email=email)

            if verify_otp(user, otp_code, purpose):
                # Handle different purposes professionally
                if purpose == 'email_verification':
                    user.is_email_verified = True
                    user.is_active = True
                    user.save()

                    try:
                        send_welcome_email(user.id)
                    except Exception as e:
                        logger.error(f"Failed to send welcome email: {str(e)}")
                        return custom_exception_handler(e, request)

                    return CustomResponse.success(
                        message='Email verified successfully',
                        data={
                            'user': UserSerializer(
                                user, context={'request': request}
                            ).data,
                        },
                        status_code=status.HTTP_200_OK
                    )

                elif purpose == 'password_reset':
                    return CustomResponse.success(
                        message=(
                            'OTP verified. You can now reset '
                            'your password.'
                        ),
                        data={'can_reset_password': True},
                        status_code=status.HTTP_200_OK
                    )

                elif purpose == 'login':
                    refresh = RefreshToken.for_user(user)
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

                elif purpose == 'change_email':
                    return CustomResponse.success(
                        message='OTP verified. You can now change your email.',
                        data={'can_change_email': True},
                        status_code=status.HTTP_200_OK
                    )
            else:
                return CustomResponse.error(
                    message='Invalid or expired OTP',
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        except User.DoesNotExist as e:
            return custom_exception_handler(e, request)
