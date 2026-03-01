from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from users.api.serializers import LogoutSerializer
from core.utils.response import (
    CustomResponse,
    custom_exception_handler
)


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
            token = RefreshToken(refresh_token)
            token.blacklist()

            return CustomResponse.success(
                message="Successfully logged out",
                status_code=status.HTTP_200_OK
            )
        except TokenError as e:
            return custom_exception_handler(e, request)
