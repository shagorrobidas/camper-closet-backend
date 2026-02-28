from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from users.api.serializers import (
    ResetPasswordSerializer,
    VerifyPasswordResetOTPSerializer
)
from users.models import User
from users.tasks import send_otp_email_task
from users.utils import (
    create_otp,
    verify_otp,
    generate_reset_token
)
from django.core.cache import cache
from django.utils import timezone
from users.utils import CustomResponse, custom_exception_handler


class RequestPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
                otp_obj = create_otp(user, 'password_reset')
                send_otp_email_task(user.id, otp_obj.otp, 'password_reset')

                # Store reset request timestamp in cache
                cache.set(
                    f"password_reset_request_{user.id}",
                    timezone.now(),
                    3600
                )

                return CustomResponse.success(
                    message="Password reset OTP has been sent",
                    data={"next_step": "verify_otp"},
                    status_code=status.HTTP_200_OK
                )

            except User.DoesNotExist as e:
                return custom_exception_handler(e)

        except Exception as e:
            return custom_exception_handler(e)


class VerifyPasswordResetOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyPasswordResetOTPSerializer

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            try:
                user = User.objects.get(email=email)
                
                if verify_otp(user, otp, 'password_reset'):
                    reset_token = generate_reset_token(user.id)
                    cache.set(
                        f"password_reset_token_{user.id}",
                        reset_token,
                        3600
                    )
                    data = {
                        "reset_token": reset_token,
                        "next_step": "set_new_password"
                    }
                    return CustomResponse.success(
                        message="OTP verified successfully",
                        data=data,
                        status_code=status.HTTP_200_OK
                    )
                else:
                    return CustomResponse.error(
                        message="Invalid or expired OTP",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

            except User.DoesNotExist as e:
                return custom_exception_handler(e)

        except Exception as e:
            return custom_exception_handler(e)
