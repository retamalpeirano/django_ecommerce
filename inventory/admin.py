from django.contrib import admin
from .models import Inventory, StockMovement


class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'stock', 'stock_minimum', 'almost_out')
    list_filter = ('product__category',)
    search_fields = ('product__product_name',)


class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'movement_type', 'quantity', 'movement_date')
    list_filter = ('movement_type', 'movement_date')
    search_fields = ('inventory__name',)  # Asumiendo que `Inventory` tiene un campo `name`
    ordering = ('-movement_date',)


admin.site.register(Inventory, InventoryAdmin)
admin.site.register(StockMovement, StockMovementAdmin)
