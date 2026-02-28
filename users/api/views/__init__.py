from .signup import RegisterParentView, RegisterChildView
from .verify_otp import VerifyOTPView
from .request_otp import RequestOTPView
from .login import LoginView
from .user_profile import (
    UserProfileView,
    UpdateUserProfileView,
    DeleteUserProfileView,
)


__all__ = [
    'RegisterParentView',
    'RegisterChildView',
    'VerifyOTPView',
    'RequestOTPView',
    'LoginView',
    'UserProfileView',
    'UpdateUserProfileView',
    'DeleteUserProfileView',
]
