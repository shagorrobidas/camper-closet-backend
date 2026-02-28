from rest_framework.generics import GenericAPIView
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework import status
from users.api.serializers import (
    ResetPasswordSerializer,
    VerifyPasswordResetOTPSerializer,
    SetNewPasswordSerializer
    
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


class SetNewPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']

            try:
                user = User.objects.get(email=email)
                reset_token = request.data.get('reset_token')
                cached_token = cache.get(f"password_reset_token_{user.id}")
                if reset_token and cached_token != reset_token:
                    return CustomResponse.error(
                        message="Invalid or expired reset token",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                user.set_password(new_password)
                user.save()
                cache.delete(f"password_reset_token_{user.id}")
                cache.delete(f"password_reset_request_{user.id}")
                return CustomResponse.success(
                    message="Password reset successfully",
                    data={"next_step": "login"},
                    status_code=status.HTTP_200_OK
                )

            except User.DoesNotExist as e:
                return custom_exception_handler(e)

        except serializers.ValidationError as e:
            return custom_exception_handler(e)

        except Exception as e:
            return custom_exception_handler(e)


class CheckPasswordResetStatusView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')
            if not email:
                return CustomResponse.error(
                    message="Email is required",
                    status_code = status.HTTP_400_BAD_REQUEST
                )
            try:
                user = User.objects.get(email=email)
                reset_request_time = cache.get(
                    f"password_reset_request_{user.id}"
                )
                if  reset_request_time:
                    time_diff = timezone.now() - reset_request_time
                    if time_diff > timedelta(hours=1):
                        data ={
                            "is_expired": True,
                            "status": "expired",
                            "can_retry": True
                        }
                        return CustomResponse.error(
                            message="Password reset request has expired",
                            data=data,
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
                    else:
                        data = {
                            "status": "pending",
                            "can_retry": False
                        }
                        return CustomResponse.success(
                            message="Password reset request is pending",
                            data=data,
                            status_code=status.HTTP_200_OK
                        )
                else:
                    data = {
                        "status": "not_found",
                        "can_retry": True
                    }
                    return CustomResponse.error(
                        message="Password reset request not found",
                        data=data,
                        status_code=status.HTTP_404_NOT_FOUND
                    )
            except User.DoesNotExist as e:
                return custom_exception_handler(e)
        except Exception as e:
            return custom_exception_handler(e)
