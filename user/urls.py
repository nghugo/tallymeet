from django.urls import path
from .views import register, profile, activate, RecapLoginView, resend_activation
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("register/", register, name="user-register"),
    path("profile/", profile, name="user-profile"),
    path("login/", RecapLoginView.as_view(template_name="user/login.html"), name="user-login"),  # settings.py LOGIN_REDIRECT_URL = "user-profile"
    path("logout/", auth_views.LogoutView.as_view(template_name="user/logout.html"), name="user-logout"),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('resend_activation/', resend_activation, name='resend-activation'),
]

