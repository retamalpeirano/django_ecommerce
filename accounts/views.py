from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserProfile
from .forms import UserForm, UserProfileForm, CustomSignupForm
from django.contrib.auth.decorators import login_required
from allauth.account.views import SignupView


# Vista para perfil de usuario
@login_required
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Crear el perfil si no existe
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)


# Vista personalizada para registro manual usando Allauth
class CustomSignupView(SignupView):
    template_name = "accounts/signup.html"
    form_class = CustomSignupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["custom_signup"] = True
        return context
