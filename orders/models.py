from django.db import models
from accounts.models import Account
from store.models import Product
from cart.models import Cart, CartItem
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _("Pendiente")),
        ('confirmed', _("Confirmado")),
        ('shipped', _("Enviado")),
        ('completed', _("Completado")),
        ('canceled', _("Cancelado")),
    ]

    user = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL)
    session = models.ForeignKey(Session, null=True, blank=True, on_delete=models.SET_NULL)
    total_price = models.DecimalField(_("Precio Total"), max_digits=10, decimal_places=2)
    status = models.CharField(_("Estado del Pedido"), max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(_("Fecha de Creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Última Actualización"), auto_now=True)

    def __str__(self):
        return f"Pedido {self.id} - Estado: {self.get_status_display()}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_("Cantidad"))
    price = models.DecimalField(_("Precio Unitario"), max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"

    def subtotal(self):
        return self.price * self.quantity
