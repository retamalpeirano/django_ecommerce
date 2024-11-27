from django.contrib import admin
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session', 'total_price', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__email', 'session__session_key')
    readonly_fields = ('created_at', 'updated_at')

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = "Precio Total"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'subtotal')
    list_filter = ('order',)
    search_fields = ('product__product_name',)
    readonly_fields = ('subtotal',)

    def subtotal(self, obj):
        return obj.subtotal()
    subtotal.short_description = "Subtotal"
