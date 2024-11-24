from django.urls import path, include
from .views import profile, CustomSignupView

urlpatterns = [
    path('', include('allauth.urls')),  # Rutas de Allauth
    path('profile/', profile, name='profile'),  # Rutas app accounts
    path('signup/', CustomSignupView.as_view(), name='custom_signup'),
]
