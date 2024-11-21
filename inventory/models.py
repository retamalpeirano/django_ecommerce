"""
    INVENTORY MODELS
"""

from django.db import models
from store.models import Product
from django.utils import timezone

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    stock = models.PositiveIntegerField(default=0)
    stock_minimum = models.PositiveIntegerField(default=0)

    def almost_out(self):
        return self.stock <= self.stock_minimum
    
    def stock_minimun_message(self):
        if self.almost_out():
            return f"Advertencia: El producto '{self.product.product_name}' está por agotarse. \nStock actual: {self.stock}"

    def __str__(self):
        return f"Inventario de {self.product.product_name}"


class StockMovement(models.Model):
    MOVEMENT_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_CHOICES)
    quantity = models.PositiveIntegerField()
    movement_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.quantity} unidades"
    
    @classmethod
    def register_movement(cls, inventory, movement_type, quantity):

        if movement_type == 'salida' and quantity > inventory.stock:
            raise ValueError("No hay suficiente stock disponible para este movimiento.")

        movement = cls.objects.create(
            inventory=inventory,
            movement_type=movement_type,
            quantity=quantity,
            movement_date=timezone.now()
        )

        if movement_type == 'entrada':
            inventory.stock += quantity
        elif movement_type == 'salida':
            inventory.stock -= quantity

        inventory.save()
        return movement