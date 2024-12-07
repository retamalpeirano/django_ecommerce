from django.contrib import admin
from .models import Order, OrderItem
from django.utils.formats import localize


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No se crean formularios vacíos por defecto
    readonly_fields = ('subtotal',)
    fields = ('product', 'quantity', 'price', 'subtotal')

    def subtotal(self, obj):
        """
        Calcula el subtotal, devolviendo 0 si los valores son nulos.
        """
        try:
            if obj and obj.price is not None and obj.quantity is not None:
                return localize(obj.price * obj.quantity)
        except (TypeError, AttributeError):
            pass
        return localize(0)  # Devuelve 0 si hay un error o valores no definidos
    subtotal.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'item_count', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    inlines = [OrderItemInline]
    actions = ['mark_as_confirmed', 'mark_as_canceled']

    def item_count(self, obj):
        """
        Cuenta los ítems asociados a la orden.
        """
        return obj.items.count()
    item_count.short_description = "Número de Ítems"

    def total_price(self, obj):
        """
        Devuelve el precio total de la orden formateado.
        """
        return localize(obj.total_price)
    total_price.short_description = "Precio Total"

    @admin.action(description="Marcar como Confirmado")
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')

    @admin.action(description="Marcar como Cancelado")
    def mark_as_canceled(self, request, queryset):
        queryset.update(status='canceled')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'subtotal')
    list_filter = ('order', 'product')
    search_fields = ('product__product_name',)
    readonly_fields = ('subtotal',)
    list_per_page = 50

    def subtotal(self, obj):
        """
        Calcula el subtotal, devolviendo 0 si los valores son nulos.
        """
        try:
            if obj and obj.price is not None and obj.quantity is not None:
                return localize(obj.price * obj.quantity)
        except (TypeError, AttributeError):
            pass
        return localize(0)  # Devuelve 0 si hay un error o valores no definidos
    subtotal.short_description = "Subtotal"
