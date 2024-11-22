"""
    ADMIN STORE
"""

from django.contrib import admin
from .models import Product, ReviewRating
from django.utils.html import format_html
from inventory.models import Inventory


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'get_stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}

    def get_stock(self, obj):
        inventory = Inventory.objects.filter(product=obj).first()
        return inventory.stock if inventory else "No definido"
    get_stock.short_description = 'Stock'

admin.site.register(Product, ProductAdmin)
admin.site.register(ReviewRating)
