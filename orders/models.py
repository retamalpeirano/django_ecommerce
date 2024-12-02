from django.db import models
from accounts.models import Account
from store.models import Product
from cart.models import Cart, CartItem
from inventory.models import StockMovement
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.db import transaction


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
    
    @classmethod
    def create_from_cart(cls, cart, user=None, session=None):
        """Crea una orden a partir de un carrito."""
        if not cart.cartitems.exists():
            raise ValueError("El carrito está vacío y no se puede crear una orden.")

        with transaction.atomic():
            order = cls.objects.create(
                user=user,
                session=session,
                total_price=cart.total_cost(),
                status='pending'
            )

            for cart_item in cart.cartitems.all():
                product = cart_item.product
                inventory = product.inventory

                if inventory.stock < cart_item.quantity:
                    raise ValueError(f"No hay suficiente stock para el producto {product.product_name}.")

                # Registrar ítems de la orden
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    price=product.price
                )

                # Descontar stock y registrar movimiento
                inventory.stock -= cart_item.quantity
                inventory.save()

                StockMovement.register_movement(
                    inventory=inventory,
                    movement_type='salida',
                    quantity=cart_item.quantity
                )

            # Vaciar el carrito
            cart.cartitems.all().delete()

        # Registrar en el log que la orden fue creada con éxito
        logger = logging.getLogger(__name__)
        logger.info(f"Orden {order.id} creada exitosamente para el usuario {user.id if user else 'anónimo'}.")

        return order


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_("Cantidad"))
    price = models.DecimalField(_("Precio Unitario"), max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"

    def subtotal(self):
        return self.price * self.quantity
