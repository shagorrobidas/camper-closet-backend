from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterParentView,
    RegisterChildView,
    VerifyOTPView,
    RequestOTPView,
    LoginView,
    UserProfileView,
    UpdateUserProfileView,
    DeleteUserProfileView,
    RequestPasswordView,
    VerifyPasswordResetOTPView,
    SetNewPasswordView,
    CheckPasswordResetStatusView,
    ChangePasswordView,
    LogoutView,
    NotificationListView,
    NotificationMarkReadView,
    NotificationSettingView,
    ManageAccountView,
    SwitchToChildView,
    SwitchToParentView,
    ProfileView,
    FirebaseAuthView
)

urlpatterns = [
    # ── Registration ─────────────────────────────────────────────────────────
    path(
        'signup/parent/',
        RegisterParentView.as_view(),
        name='signup_parent',
    ),
    path(
        'signup/child/',
        RegisterChildView.as_view(),
        name='signup_child',
    ),

    path(
        'verify-otp/',
        VerifyOTPView.as_view(),
        name='verify_otp'
    ),
    path(
        'request-otp/',
        RequestOTPView.as_view(),
        name='request_otp'
    ),

    # ── Login ──────────────────────────
    path(
        'login/',
        LoginView.as_view(),
        name='login'
    ),
    path(
        'login/firebase/',
        FirebaseAuthView.as_view(),
        name='login-firebase'
    ),
    # ── Password Reset ──────────────────────────
    path(
        'change-password/',
        ChangePasswordView.as_view(),
        name='change_password'
    ),
    path(
        'request-password-reset/',
        RequestPasswordView.as_view(),
        name='request_password-reset'
    ),
    path(
        'verify-password-reset-otp/',
        VerifyPasswordResetOTPView.as_view(),
        name='verify_password_reset_otp'
    ),
    path(
        'set-new-password/',
        SetNewPasswordView.as_view(),
        name='set_new_password'
    ),
    path(
        'check-reset-status/',
        CheckPasswordResetStatusView.as_view(),
        name='check_reset_status'
    ),

    # ── Profile ──────────────────────────
    path(
        'profile/',
        UserProfileView.as_view(),
        name='profile'
    ),
    path(
        'profile/<uuid:pk>/',
        UserProfileView.as_view(),
        name='profile_detail'
    ),
    path(
        'profile/update/',
        UpdateUserProfileView.as_view(),
        name='profile_update'
    ),
    path(
        'profile/update/<uuid:pk>/',
        UpdateUserProfileView.as_view(),
        name='profile_update_detail'
    ),
    path(
        'profile/delete/',
        DeleteUserProfileView.as_view(),
        name='profile_delete'
    ),
    path(
        'profile/delete/<uuid:pk>/',
        DeleteUserProfileView.as_view(),
        name='profile_delete_detail'
    ),
    path(
        'profile/manage-account/',
        ManageAccountView.as_view(),
        name='manage_account'
    ),
    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),
    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    # path(
    #     'social-auth/google/',
    #     GoogleSocialAuthView.as_view(),
    #     name='google_social_auth'
    # ),
    # path(
    #     'social-auth/apple/',
    #     AppleSocialAuthView.as_view(),
    #     name='apple_social_auth'
    # ),

    # ── Notifications ──────────────────────────
    path(
        'notifications/',
        NotificationListView.as_view(),
        name='notification-list'
    ),
    path(
        'notifications/mark-read/',
        NotificationMarkReadView.as_view(),
        name='notification-mark-all-read'
    ),
    path(
        'notifications/<uuid:pk>/mark-read/',
        NotificationMarkReadView.as_view(),
        name='notification-mark-read'
    ),
    path(
        'notifications/settings/',
        NotificationSettingView.as_view(),
        name='notification-settings'
    ),

    # ── Switch Account ──────────────────────────
    path(
        'switch-to-child/',
        SwitchToChildView.as_view(),
        name='switch_to_child'
    ),
    path(
        'switch-to-parent/',
        SwitchToParentView.as_view(),
        name='switch_to_parent'
    ),
    path(
        'profile/me/',
        ProfileView.as_view(),
        name='profile'
    ),
]
