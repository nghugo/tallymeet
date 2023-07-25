from django.urls import path
from .views import register, profile

urlpatterns = [
    path("register/", register, name="user-register"),
    path("profile/", profile, name="user-profile"),
]


