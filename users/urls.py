from django.urls import path
from django.contrib.auth import views

from .views import SignUpView, SignInView, ConfirmCodeView, PasswordResetView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('confirm_code/', ConfirmCodeView.as_view(), name='confirm_code'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]