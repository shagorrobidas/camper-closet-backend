from django.urls import path
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
    SetNewPasswordView
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
    path(
        'login/',
        LoginView.as_view(),
        name='login'
    ),
    # path(
    #     'change-password/',
    #     ChangePasswordView.as_view(),
    #     name='change_password'
    # ),
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
    # path(
    #     'check-reset-status/',
    #     CheckPasswordResetStatusView.as_view(),
    #     name='check_reset_status'
    # ),

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
    # path(
    #     'logout/',
    #     LogoutView.as_view(),
    #     name='logout'
    # ),
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

]
