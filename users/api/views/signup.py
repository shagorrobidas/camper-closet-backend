import logging
from rest_framework import generics, status, permissions
from rest_framework.throttling import ScopedRateThrottle
from users.models import User
from users.api.serializers import (
    RegisterParentSerializer,
    RegisterChildSerializer,
)
from users.utils import create_otp
from users.tasks import (
    send_otp_email_task,
    send_child_credentials_email_task,
)
from core.utils.response import CustomResponse
from core.utils.exceptions import custom_exception_handler

logger = logging.getLogger('user')


# ── Parent registration ──────────────────────────────────────────────────────

class RegisterParentView(generics.CreateAPIView):
    """
    Register a new **parent** account.

    Open to unauthenticated users (AllowAny).
    The serializer automatically sets role='parent'.
    After creation an OTP is sent for email verification.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterParentSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            logger.info(f"New parent registered: {user.email}")

            otp_obj = create_otp(user, 'email_verification')
            send_otp_email_task(user.id, otp_obj.otp, 'email_verification')

            return CustomResponse.success(
                message=(
                    "Parent account created successfully. "
                    "Please verify your email."
                ),
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return custom_exception_handler(e, request)


# ── Child registration ───────────────────────────────────────────────────────

class RegisterChildView(generics.CreateAPIView):
    """
    Register a new **child** account under the authenticated parent.

    - Requires authentication (IsAuthenticated).
    - The authenticated user must have role='parent'.
    - The new child is automatically linked to the requesting parent.
    - Child is pre-verified — no OTP email is sent.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RegisterChildSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request, *args, **kwargs):
        try:
            # Only parent accounts may create children
            if request.user.role != 'parent':
                return CustomResponse.error(
                    message=(
                        "Only parent accounts can register"
                        " child accounts."
                    ),
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            # Inject the authenticated parent into serializer context
            serializer = self.get_serializer(
                data=request.data,
                context={
                    **self.get_serializer_context(),
                    'parent': request.user,
                },
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # The raw password that was used during creation
            raw_password = request.data.get('password')
            if raw_password:
                send_child_credentials_email_task(user.id, raw_password)

            logger.info(
                f"New child registered: {user.email} "
                f"under parent: {request.user.email}"
            )

            return CustomResponse.success(
                message="Child account created successfully.",
                status_code=status.HTTP_201_CREATED,
                data=serializer.data,
            )
        except Exception as e:
            return custom_exception_handler(e, request)
