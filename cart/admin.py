from django.contrib import admin
from .models import Cart, CartItem
from django.contrib.sessions.models import Session


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session', 'total_items', 'total_cost', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'session__session_key')
    readonly_fields = ('total_items', 'total_cost', 'created_at', 'updated_at')

    def total_items(self, obj):
        return obj.total_items()
    total_items.short_description = "Total de Productos"

    def total_cost(self, obj):
        return obj.total_cost()
    total_cost.short_description = "Costo Total"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'subtotal')
    list_filter = ('cart',)
    search_fields = ('product__product_name',)
    readonly_fields = ('subtotal',)

    def subtotal(self, obj):
        return obj.subtotal()
    subtotal.short_description = "Subtotal"

## SESSIONS##

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
