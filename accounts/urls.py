from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView , TokenBlacklistView


urlpatterns = [
    # User registration and OTP verification
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify_otp'),

    # Login 
    path('login/', views.MyTokenObtainPairView.as_view(), name='login'),

    # change-password-with-old-password
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password-with-old-password'),

    # change-password-with-otp
    path('request-otp/', views.RequestOTPView.as_view(), name='request_password_reset_otp'),
    path('request-password-reset-otp/', views.VerifyOTPForPasswordChangeView.as_view(), name='reset_password'),


    # User profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),


    # Token management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # logout
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # Miscellaneous
    path('test/', views.testEndPoint, name='test'),
    path('', views.getRoutes),
]
