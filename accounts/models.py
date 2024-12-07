from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("El usuario debe tener un correo electrónico válido"))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.update({'is_staff': True, 'is_superuser': True})
        return self.create_user(email, password, **extra_fields)

class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("correo electrónico"), unique=True, max_length=255)
    username = models.CharField(_("nombre de usuario"), max_length=50, unique=True, blank=False)  # Agregado
    first_name = models.CharField(_("nombre"), max_length=50, blank=True)
    last_name = models.CharField(_("apellido"), max_length=50, blank=True)

    is_active = models.BooleanField(_("activo"), default=True)
    is_staff = models.BooleanField(_("es miembro del staff"), default=False)
    is_superuser = models.BooleanField(_("es superusuario"), default=False)
    is_customer = models.BooleanField(_("es cliente"), default=True)

    date_joined = models.DateTimeField(_("fecha de registro"), auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # Agregado

    objects = AccountManager()

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="profile")
    rut = models.CharField(_("RUT o identificación nacional"), max_length=20, blank=True)
    profile_picture = models.ImageField(_("foto de perfil"), upload_to="user_profiles/", blank=True)
    address = models.JSONField(_("dirección"), default=dict, blank=True)
    phone_number = models.CharField(_("número de teléfono"), max_length=15, blank=True)
    additional_data = models.JSONField(_("datos adicionales"), default=dict, blank=True)

    def __str__(self):
        return self.user.email

