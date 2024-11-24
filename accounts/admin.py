from django.contrib import admin
from .models import Account, UserProfile

# Admin configuration for Account
class AccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        ('Personal Info', {
            'fields': ('email', 'username', 'first_name', 'last_name')  # Eliminado 'phone_number'
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_customer')  # Eliminado 'is_superadmin'
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login')  # Solo lectura
        }),
    )

    add_fieldsets = (
        ('Personal Info', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        """Devuelve fieldsets apropiados según si el objeto existe o no"""
        if obj:  # Editando un usuario existente
            return self.fieldsets
        return self.add_fieldsets

# Métodos para extraer valores de la dirección en UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_city', 'get_state', 'get_country', 'get_full_address')
    search_fields = ('user__email', 'user__username', 'address__city', 'address__state', 'address__country')
    ordering = ('user__email',)

    def get_city(self, obj):
        return obj.address.get('city', '')
    get_city.short_description = 'City'

    def get_state(self, obj):
        return obj.address.get('state', '')
    get_state.short_description = 'State'

    def get_country(self, obj):
        return obj.address.get('country', '')
    get_country.short_description = 'Country'

    def get_full_address(self, obj):
        return obj.get_full_address()
    get_full_address.short_description = 'Full Address'

# Registering models with admin
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
