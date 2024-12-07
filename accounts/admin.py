from django.contrib import admin
from .models import Account, UserProfile
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _


# Admin configuration for Account
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _("Perfiles de Usuario")
    fk_name = "user"


class AccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_customer', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (_("Información Personal"), {
            'fields': ('email', 'username', 'first_name', 'last_name')
        }),
        (_("Permisos"), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_customer')
        }),
        (_("Fechas Importantes"), {
            'fields': ('date_joined', 'last_login')
        }),
    )

    inlines = [UserProfileInline]

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.fieldsets
        return (
            (_("Información Personal"), {
                'classes': ('wide',),
                'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
            }),
        )


# Admin configuration for UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rut', 'phone_number', 'get_full_address')
    search_fields = ('user__email', 'rut', 'phone_number')
    ordering = ('user__email',)

    def get_full_address(self, obj):
        address = obj.get_full_address()
        return address if address.strip() else _("Dirección no especificada")
    get_full_address.short_description = _("Dirección completa")


# Admin configuration for Session
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'user', 'expire_date')
    readonly_fields = ('session_key', 'user', 'expire_date')
    search_fields = ('session_key',)

    def user(self, obj):
        """
        Devuelve el email del usuario asociado a la sesión, si existe.
        """
        try:
            from django.contrib.sessions.backends.db import SessionStore
            session_data = SessionStore(session_key=obj.session_key).load()
            user_id = session_data.get('_auth_user_id')
            if user_id:
                from accounts.models import Account
                return Account.objects.filter(id=user_id).values_list('email', flat=True).first() or _("Usuario eliminado")
        except Exception:
            return _("Usuario no autenticado")


# Register models with the admin
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
