from .signup import RegisterParentView, RegisterChildView
from .verify_otp import VerifyOTPView
from .request_otp import RequestOTPView
from .login import LoginView
from .user_profile import (
    UserProfileView,
    UpdateUserProfileView,
    DeleteUserProfileView,
    ManageAccountView
)
from .request_password import (
    RequestPasswordView,
    VerifyPasswordResetOTPView,
    SetNewPasswordView,
    CheckPasswordResetStatusView
)
from .change_password import ChangePasswordView
from .logout import LogoutView
from .notification import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationSettingView,
)
from .switch_account import (
    SwitchToChildView,
    SwitchToParentView,
    ProfileView
)
from.social_auth import FirebaseAuthView


__all__ = [
    'RegisterParentView',
    'RegisterChildView',
    'VerifyOTPView',
    'RequestOTPView',
    'LoginView',
    'UserProfileView',
    'UpdateUserProfileView',
    'DeleteUserProfileView',
    'RequestPasswordView',
    'VerifyPasswordResetOTPView',
    'SetNewPasswordView',
    'CheckPasswordResetStatusView',
    'ChangePasswordView',
    'LogoutView',
    'NotificationListView',
    'NotificationMarkReadView',
    'NotificationSettingView',
    'ManageAccountView',
    'SwitchToChildView',
    'SwitchToParentView',
    'ProfileView',
    'FirebaseAuthView',
]
