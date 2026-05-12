from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from users.api.serializers import FirebaseAuthSerializer
from core.utils import CustomResponse

class FirebaseAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FirebaseAuthSerializer(data=request.data)
        if serializer.is_valid():
            return CustomResponse.success(
                message="Login successful",
                data=serializer.validated_data,
                status_code=status.HTTP_200_OK,
            )
        return CustomResponse.error(
            message="Invalid token",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )