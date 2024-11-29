from django.urls import path, include
from .views import profile
from django.contrib.auth.views import PasswordResetView, PasswordChangeView

urlpatterns = [
    path('', include('allauth.urls')),
    path('profile/', profile, name='profile'),
    path('reset-password/', PasswordResetView.as_view(template_name='accounts/resetPassword.html'), name='reset_password'),
    path('change-password/', PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),
]
