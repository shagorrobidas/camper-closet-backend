from django.urls import path
from .views import (
    RegisterView,
    VerifyOTPView,
    RequestOTPView,
    LoginView,
    # ChangePasswordView,
    # RequestPasswordResetView,
    # VerifyPasswordResetOTPView,
    # SetNewPasswordView,
    # CheckPasswordResetStatusView,
    # LogoutView,
    # UserProfileView,
    # UserProfileUpdateView,
    # UserProfileDeleteView,
    # RequestEmailChangeView,
    # VerifyEmailChangeView,
    # GoogleSocialAuthView,
    # AppleSocialAuthView
)

urlpatterns = [
    path(
        'signup/',
        RegisterView.as_view(),
        name='signup'
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
    # path(
    #     'request-password-reset/',
    #     RequestPasswordResetView.as_view(),
    #     name='request_password-reset'
    # ),
    # path(
    #     'verify-password-reset-otp/',
    #     VerifyPasswordResetOTPView.as_view(),
    #     name='verify_password_reset_otp'
    # ),
    # path(
    #     'set-new-password/',
    #     SetNewPasswordView.as_view(),
    #     name='set_new_password'
    # ),
    # path(
    #     'check-reset-status/',
    #     CheckPasswordResetStatusView.as_view(),
    #     name='check_reset_status'
    # ),

    # path(
    #     'profile/',
    #     UserProfileView.as_view(),
    #     name='profile'
    # ),
    # path(
    #     'profile/update/',
    #     UserProfileUpdateView.as_view(),
    #     name='profile_update'
    # ),
    # path(
    #     'profile/delete/',
    #     UserProfileDeleteView.as_view(),
    #     name='profile_delete'
    # ),
    # path(
    #     'logout/',
    #     LogoutView.as_view(),
    #     name='logout'
    # ),
    # path(
    #     'change-email/request/',
    #     RequestEmailChangeView.as_view(),
    #     name='request_email_change'
    # ),
    # path(
    #     'change-email/verify/',
    #     VerifyEmailChangeView.as_view(),
    #     name='verify_email_change'
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
