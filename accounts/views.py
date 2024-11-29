
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile
from .forms import UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required


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

@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')  # Ajusta la plantilla si es necesario

