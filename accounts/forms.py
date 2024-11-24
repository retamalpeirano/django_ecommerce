from django import forms
from .models import UserProfile
from django.contrib.auth import get_user_model
from allauth.account.forms import SignupForm

User = get_user_model()

# Formulario para editar perfil de usuario
class UserProfileForm(forms.ModelForm):
    address_line_1 = forms.CharField(required=False, label="Dirección Línea 1")
    address_line_2 = forms.CharField(required=False, label="Dirección Línea 2")
    city = forms.CharField(required=False, label="Ciudad")
    state = forms.CharField(required=False, label="Estado/Provincia")
    country = forms.CharField(required=False, label="País")

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'address_line_1', 'address_line_2', 'city', 'state', 'country']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.address:
            address = self.instance.address
            self.fields['address_line_1'].initial = address.get('line1', '')
            self.fields['address_line_2'].initial = address.get('line2', '')
            self.fields['city'].initial = address.get('city', '')
            self.fields['state'].initial = address.get('state', '')
            self.fields['country'].initial = address.get('country', '')

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user_profile = super(UserProfileForm, self).save(commit=False)
        user_profile.address = {
            'line1': self.cleaned_data.get('address_line_1', ''),
            'line2': self.cleaned_data.get('address_line_2', ''),
            'city': self.cleaned_data.get('city', ''),
            'state': self.cleaned_data.get('state', ''),
            'country': self.cleaned_data.get('country', ''),
        }
        if commit:
            user_profile.save()
        return user_profile

# Formulario para editar datos básicos del usuario
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

# Formulario para registro manual
class CustomSignupForm(SignupForm):
    username = forms.CharField(max_length=50, required=True, label="Nombre de usuario")
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user
