from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.db import transaction
from .models import Cart, get_or_create_cart


@receiver(user_logged_in)
def sync_cart_to_user(sender, request, user, **kwargs):
    """Sincroniza el carrito de la sesión con el usuario autenticado."""
    session_cart = get_or_create_cart(request)

    # Si no hay carrito de sesión o ya está asociado a un usuario, no hacemos nada
    if not session_cart.session or session_cart.user:
        return

    try:
        with transaction.atomic():
            # Intentar buscar un carrito existente para el usuario
            user_cart, created = Cart.objects.get_or_create(user=user)

            if not created:
                # Combinar ítems del carrito de sesión al carrito del usuario
                for item in session_cart.cartitems.all():
                    existing_item = user_cart.cartitems.filter(product=item.product).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        item.cart = user_cart
                        item.save()

            # Eliminar el carrito de sesión después de transferir sus ítems
            session_cart.delete()

            # Finalmente, desvincular la sesión del carrito si aún no lo está
            user_cart.session = None
            user_cart.save()

    except Exception as e:
        # Registrar el error en caso de fallo
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al sincronizar carrito para el usuario {user.id}: {e}")
