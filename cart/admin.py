from django.contrib import admin
from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_or_session', 'total_items', 'total_cost', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'session__session_key')
    readonly_fields = ('total_items', 'total_cost', 'created_at', 'updated_at')
    actions = ['clear_cart']
    list_per_page = 50

    def get_user_or_session(self, obj):
        if obj.user:
            return obj.user.email
        if obj.session:
            return f"Sesión: {obj.session.session_key}"
        return "Sin usuario ni sesión"
    get_user_or_session.short_description = "Usuario o Sesión"

    def total_items(self, obj):
        return obj.total_items()
    total_items.short_description = "Total de Productos"

    def total_cost(self, obj):
        return obj.total_cost()
    total_cost.short_description = "Costo Total"

    @admin.action(description="Vaciar carrito")
    def clear_cart(self, request, queryset):
        for cart in queryset:
            cart.cartitems.all().delete()


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'subtotal', 'is_out_of_stock')
    list_filter = ('cart', 'product')
    search_fields = ('product__product_name',)
    readonly_fields = ('subtotal',)
    list_per_page = 50

    def subtotal(self, obj):
        from django.utils.formats import localize
        return localize(obj.subtotal())
    subtotal.short_description = "Subtotal"

    def is_out_of_stock(self, obj):
        return obj.product.inventory.stock < obj.quantity
    is_out_of_stock.boolean = True
    is_out_of_stock.short_description = "Sin stock"
