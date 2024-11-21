from django.contrib import admin
from .models import Inventory

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'stock', 'stock_minimum', 'almost_out')
    list_filter = ('product__category',)
    search_fields = ('product__product_name',)

admin.site.register(Inventory, InventoryAdmin)
