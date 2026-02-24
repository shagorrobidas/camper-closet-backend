from rest_framework import (
    generics,
    status,
    permissions,
    serializers
)
from users.models import User
from users.api.serializers import (
    OTPSerializer,
)
from users.utils import create_otp
from users.tasks import send_otp_email_task
from core.utils.response import CustomResponse
from core.utils.exceptions import custom_exception_handler
import logging

logger = logging.getLogger(__name__)


class RequestOTPView(generics.GenericAPIView):
    """
    View to request OTP for various purposes.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = OTPSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email']
            purpose = serializer.validated_data['purpose']

            try:
                user = User.objects.get(email=email)

                # Business logic checks
                if purpose == 'email_verification' and user.is_email_verified:
                    return CustomResponse.error(
                        message="Email is already verified",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                # Create and send OTP
                otp_obj = create_otp(user, purpose)
                send_otp_email_task(user.id, otp_obj.otp, purpose)

                return CustomResponse.success(
                    message=f"OTP sent to {email} for {purpose.replace('_', ' ')}",
                    status_code=status.HTTP_200_OK
                )
            except User.DoesNotExist as e:
                return custom_exception_handler(e, request)
        except Exception as e:
            logger.error(f"Failed to request OTP: {str(e)}")
            return custom_exception_handler(e, request)
