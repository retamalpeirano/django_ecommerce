# Django
from django.urls import path, include, reverse_lazy
from django.views.generic.base import RedirectView
from django.contrib.auth.views import PasswordResetView, PasswordChangeView

# Local
from . import views


urlpatterns = [

    path('login/', RedirectView.as_view(url=reverse_lazy('google_login')), name='account_login'),

    path('', include('allauth.urls')),
    path('dashboard/', views.dashboard, name='account_dashboard'),
    path('account/', views.account_view, name='account_view'),
    path('account/delete/', views.delete_account, name='delete_account'),
    path('reset-password/', PasswordResetView.as_view(template_name='accounts/resetPassword.html'), name='reset_password'),
    path('change-password/', PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),
]
