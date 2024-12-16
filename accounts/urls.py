from django.urls import path, include
from . import views
from django.contrib.auth.views import PasswordResetView, PasswordChangeView

urlpatterns = [
    path('', include('allauth.urls')),
    path('dashboard/', views.dashboard, name='account_dashboard'),
    path('account/', views.account_view, name='account_view'),
    path('account/delete/', views.delete_account, name='delete_account'),
    path('reset-password/', PasswordResetView.as_view(template_name='accounts/resetPassword.html'), name='reset_password'),
    path('change-password/', PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),
]
