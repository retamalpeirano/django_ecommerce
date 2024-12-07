from django.contrib import admin
from .models import Cart, CartItem


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

