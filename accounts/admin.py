from django.contrib import admin
from .models import Account, UserProfile
from django.contrib.sessions.models import Session


# Admin configuration for Account
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profiles'
    fk_name = 'user'


class AccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        ('Personal Info', {
            'fields': ('email', 'username', 'first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_customer')
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login')
        }),
    )

    inlines = [UserProfileInline]  # Añade el perfil de usuario como inline

    def get_fieldsets(self, request, obj=None):
        """Devuelve fieldsets apropiados según si el objeto existe o no"""
        if obj:  # Editando un usuario existente
            return self.fieldsets
        return (
            ('Personal Info', {
                'classes': ('wide',),
                'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
            }),
        )


# Admin configuration for UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'get_full_address', 'rut')
    search_fields = ('user__email', 'phone_number', 'rut')
    ordering = ('user__email',)

    def get_full_address(self, obj):
        return obj.get_full_address()
    get_full_address.short_description = 'Full Address'


## SESSIONS ##
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'user', 'expire_date')
    readonly_fields = ('session_key', 'user', 'expire_date')
    search_fields = ('session_key',)

    def user(self, obj):
        # Intenta extraer el usuario de los datos de la sesión
        from django.contrib.sessions.backends.db import SessionStore
        session_data = SessionStore(session_key=obj.session_key).load()
        user_id = session_data.get('_auth_user_id')
        if user_id:
            from accounts.models import Account
            try:
                user = Account.objects.get(id=user_id)
                return user.email
            except Account.DoesNotExist:
                return "Usuario eliminado"
        return "Usuario no autenticado"


# Registering models with admin
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
