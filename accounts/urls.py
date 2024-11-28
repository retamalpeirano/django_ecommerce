from django.urls import path, include
from .views import profile, CustomSignupView
from django.contrib.auth.views import PasswordResetView, PasswordChangeView

app_name = 'accounts'

urlpatterns = [
    path('', include('allauth.urls')),
    path('profile/', profile, name='profile'),
    path('signup/', CustomSignupView.as_view(), name='custom_signup'),
    path('reset-password/', PasswordResetView.as_view(template_name='accounts/resetPassword.html'), name='reset_password'),
    path('change-password/', PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),
]
