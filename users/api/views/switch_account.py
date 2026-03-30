from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.models import User
from users.api.serializers import SwitchChildSerializer, SwitchParentSerializer
from users.utils import get_tokens_for_user, blacklist_token
from core.utils import CustomResponse, custom_exception_handler
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.utils import datetime_from_epoch


class SwitchToChildView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = SwitchChildSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            child_id = serializer.validated_data['child_id']
            refresh_token = serializer.validated_data['refresh']

            if not request.user.is_parent:
                return CustomResponse.error(
                    message="You are not authorized to switch to child account",  # noqa
                    status_code=status.HTTP_403_FORBIDDEN
                )

            try:
                child = User.objects.get(
                    id=child_id,
                    parent=request.user,
                    role='child'
                )
            except User.DoesNotExist:
                return CustomResponse.error(
                    message="Child not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            blacklist_token(refresh_token)
            
            # Manual Blacklist Access Token in Database
            access_token = request.auth
            auth_header = request.headers.get('Authorization', '')
            if access_token and auth_header.startswith('Bearer '):
                try:
                    raw_token = auth_header.split(' ')[1]
                    outstanding_token, _ = OutstandingToken.objects.get_or_create(
                        jti=access_token.get('jti'),
                        defaults={
                            'token': raw_token,
                            'user': request.user,
                            'created_at': datetime_from_epoch(access_token.get('iat')),
                            'expires_at': datetime_from_epoch(access_token.get('exp')),
                        }
                    )
                    BlacklistedToken.objects.get_or_create(token=outstanding_token)
                except Exception:
                    pass

            # Use the new last_logout mechanism to invalidate parent's access token
            request.user.last_logout = timezone.now()
            request.user.save(update_fields=['last_logout'])

            tokens = get_tokens_for_user(child, switched_by=request.user)
            return CustomResponse.success(
                message="Switched to child account successfully",
                status_code=status.HTTP_200_OK,
                data=tokens
            )
        except Exception as e:
            return custom_exception_handler(e, {'request': request})


class SwitchToParentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = SwitchParentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            refresh_token = serializer.validated_data['refresh']

            parent = request.user.parent if request.user.is_child else request.user   # noqa
            if request.user.is_child and not parent:
                return CustomResponse.error(
                    message="You are not authorized to switch to parent account",    # noqa
                    status_code=status.HTTP_403_FORBIDDEN
                )

            # Manual Blacklist Access Token in Database
            access_token = request.auth
            auth_header = request.headers.get('Authorization', '')
            if access_token and auth_header.startswith('Bearer '):
                try:
                    raw_token = auth_header.split(' ')[1]
                    outstanding_token, _ = OutstandingToken.objects.get_or_create(
                        jti=access_token.get('jti'),
                        defaults={
                            'token': raw_token,
                            'user': request.user,
                            'created_at': datetime_from_epoch(access_token.get('iat')),
                            'expires_at': datetime_from_epoch(access_token.get('exp')),
                        }
                    )
                    BlacklistedToken.objects.get_or_create(token=outstanding_token)
                except Exception:
                    pass

            # Update last_logout to invalidate current access tokens
            request.user.last_logout = timezone.now()
            request.user.save(update_fields=['last_logout'])

            blacklist_token(refresh_token)

            tokens = get_tokens_for_user(parent)
            return CustomResponse.success(
                message="Switched to parent account successfully",
                status_code=status.HTTP_200_OK,
                data=tokens
            )
        except Exception as e:
            return custom_exception_handler(e, {'request': request})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.auth
        return CustomResponse.success("User profile retrieved", data={
            'id': request.user.id,
            'email': request.user.email,
            'full_name': request.user.full_name,
            'role': request.user.role,
            'parent_id': request.user.parent.id if request.user.parent else None, # noqa
            'is_email_verified': request.user.is_email_verified,
            'switched_by': token.get('switched_by'),
            'is_switched': token.get('is_switched', False),
        })
