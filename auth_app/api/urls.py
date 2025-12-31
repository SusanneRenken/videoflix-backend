from django.urls import path
from .views import RegistrationView, ActivateView, LoginView, LogoutView, RefreshTokenView, PasswordResetView, ConfirmPasswordView

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("activate/<uidb64>/<token>/", ActivateView.as_view(), name="activate"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password_confirm/<uidb64>/<token>/", ConfirmPasswordView.as_view(), name="password_confirm"),
]
