import logging
from rest_framework import generics, status, permissions
from rest_framework.throttling import ScopedRateThrottle
from users.models import User
from users.api.serializers import RegisterSerializer
from users.utils import create_otp
from users.tasks import send_otp_email_task
from core.utils.response import CustomResponse
from core.utils.exceptions import custom_exception_handler

logger = logging.getLogger('user')


class RegisterView(generics.CreateAPIView):
    """
    Standard user registration view.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            logger.info(f"New user registered: {user.email}")

            # Generate and send OTP for email verification
            otp_obj = create_otp(user, 'email_verification')
            send_otp_email_task(user.id, otp_obj.otp, 'email_verification')

            return CustomResponse.success(
                message="User registered successfully. Please verify your email.",
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return custom_exception_handler(e, request)
