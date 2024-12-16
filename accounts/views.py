# Django
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Local
from .models import UserProfile
from .forms import UserForm, UserProfileForm 


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

@login_required
def account_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Tu perfil ha sido actualizado correctamente.")
            return redirect('account_view')
        else:
            messages.error(request, "Corrige los errores en el formulario.")

    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'accounts/account_view.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': profile,
    })


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()
        messages.success(request, "Tu cuenta ha sido desactivada correctamente.")
        return redirect('account_logout')

    return render(request, 'accounts/account_confirm_delete.html')
