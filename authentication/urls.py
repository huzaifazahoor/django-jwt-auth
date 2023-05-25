from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import user_create, user_login, password_reset
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("signup/", user_create, name="signup"),
    path("login/", user_login, name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("password_reset/", password_reset, name="password_reset"),
]
