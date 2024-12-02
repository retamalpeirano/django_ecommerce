from django.db import models, transaction
from accounts.models import Account
from store.models import Product
#from inventory.models import Inventory # NO ESTA USANDOSE ACTUALMENTE
#from django.utils import timezone # NO ESTA USANDOSE ACTUALMENTE
from django.contrib.sessions.models import Session


# Modelo para el carrito
class Cart(models.Model):
    user = models.OneToOneField(Account, null=True, blank=True, on_delete=models.CASCADE)
    session = models.OneToOneField(Session, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {'usuario' if self.user else 'sesión'} - {self.id}"

    def total_items(self):
        """Calcula el número total de productos en el carrito."""
        return sum(item.quantity for item in self.cartitems.all())

    def total_cost(self):
        """Calcula el costo total del carrito."""
        return sum(item.subtotal() for item in self.cartitems.all())


# Modelo para los productos dentro del carrito
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cartitems', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} unidades"

    def subtotal(self):
        """Calcula el subtotal para este producto."""
        return self.product.price * self.quantity


# Excepciones personalizadas
class CartError(Exception):
    """Excepción base para errores relacionados con el carrito."""
    pass

class StockError(CartError):
    """Excepción para errores de inventario."""
    pass


# Funciones auxiliares para el carrito
def get_or_create_cart(request):
    """Obtiene o crea un carrito para un usuario autenticado o una sesión."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session, _ = Session.objects.get_or_create(session_key=request.session.session_key)
        cart, created = Cart.objects.get_or_create(session=session)
    return cart


def add_to_cart(cart, product, quantity=1):
    """Agrega un producto al carrito, verificando disponibilidad y stock."""
    if not product.is_available:
        raise CartError("Este producto no está disponible.")
    
    inventory = product.inventory
    if inventory and inventory.stock < quantity:
        raise StockError("No hay suficiente stock para este producto.")
    
    with transaction.atomic():
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        cart_item.save()

        # Actualizar stock en inventario
        inventory.stock -= quantity
        inventory.save()
    
    return cart_item


def update_cart_item(cart_item, quantity):
    """Actualiza la cantidad de un producto en el carrito o lo elimina si la cantidad es cero."""
    if quantity <= 0:
        remove_from_cart(cart_item)
    else:
        inventory = cart_item.product.inventory
        with transaction.atomic():
            if inventory and inventory.stock + cart_item.quantity < quantity:
                raise StockError("Stock insuficiente para actualizar la cantidad.")
            
            # Revertir stock anterior y descontar nueva cantidad
            inventory.stock += cart_item.quantity  # Revertir cantidad actual
            inventory.stock -= quantity  # Aplicar nueva cantidad
            inventory.save()

            cart_item.quantity = quantity
            cart_item.save()


def remove_from_cart(cart_item):
    """Elimina un producto del carrito y restaura el stock."""
    with transaction.atomic():
        inventory = cart_item.product.inventory
        if inventory:
            inventory.stock += cart_item.quantity
            inventory.save()
        cart_item.delete()
