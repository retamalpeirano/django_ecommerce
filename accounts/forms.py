from django import forms
from .models import Account, UserProfile


# Formulario para editar datos básicos del usuario
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name']  # Excluimos email para evitar su edición

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


# Formulario para editar información del perfil de usuario
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone_number', 'address', 'rut']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # Añadir clase CSS a todos los campos
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
