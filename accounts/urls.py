from django.urls import path, include
from .views import profile, CustomSignupView
from django.contrib.auth.views import PasswordResetView

app_name = 'accounts'

urlpatterns = [
    path('', include('allauth.urls')),
    path('signup/', CustomSignupView.as_view(), name='custom_signup'),
    path('reset-password/', PasswordResetView.as_view(), name='reset_password'),
]
