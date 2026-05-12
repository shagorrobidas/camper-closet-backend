from .signup import (
    RegisterParentSerializer,
    RegisterChildSerializer,
)
from .otp import (
    OTPSerializer,
    OTPVerificationSerializer
)
from .users import UserSerializer, ManageAccountSerializer
from .child import ChildSerializer
from .login import LoginSerializer
from .reset_password import (
    ResetPasswordSerializer,
    VerifyPasswordResetOTPSerializer,
    SetNewPasswordSerializer
)
from .change_password import ChangePasswordSerializer
from .logout import LogoutSerializer
from .notification import NotificationSerializer, NotificationSettingSerializer
from .switch_account import SwitchChildSerializer, SwitchParentSerializer
from .social_auth import FirebaseAuthSerializer

__all__ = [
    'RegisterSerializer',
    'RegisterParentSerializer',
    'RegisterChildSerializer',
    'OTPSerializer',
    'OTPVerificationSerializer',
    'UserSerializer',
    'ManageAccountSerializer',
    'ChildSerializer',
    'LoginSerializer',
    'ResetPasswordSerializer',
    'VerifyPasswordResetOTPSerializer',
    'SetNewPasswordSerializer',
    'ChangePasswordSerializer',
    'LogoutSerializer',
    'NotificationSerializer',
    'NotificationSettingSerializer',
    'SwitchChildSerializer',
    'SwitchParentSerializer',
]
