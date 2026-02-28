from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from users.api.serializers import ResetPasswordSerializer
from users.models import User
from users.tasks import send_otp_email_task
from users.utils import create_otp
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


