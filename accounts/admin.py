"""
from allauth.account.models import EmailAddress
from django.contrib import admin

class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'verified', 'primary')
    search_fields = ('email', 'user__username')
    list_filter = ('verified', 'primary')

admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, EmailAddressAdmin)
"""
from django.contrib import admin
from allauth.account.models import EmailAddress
from .models import Account, UserProfile


# Admin configuration for Account
class AccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superadmin')
    list_filter = ('is_active', 'is_staff', 'is_superadmin', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = (
        ('Personal Info', {
            'fields': ('email', 'username', 'first_name', 'last_name', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superadmin', 'is_customer')
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login')
        }),
    )
    add_fieldsets = (
        ('Personal Info', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'phone_number', 'password1', 'password2'),
        }),
    )


# Admin configuration for UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state', 'country', 'full_address')
    search_fields = ('user__email', 'user__username', 'city', 'state', 'country')
    ordering = ('user__email',)


# Admin configuration for EmailAddress
class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'verified', 'primary')
    search_fields = ('email', 'user__username')
    list_filter = ('verified', 'primary')


# Registering models with admin
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

# Unregister the default EmailAddress admin to use a custom one
admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, EmailAddressAdmin)
