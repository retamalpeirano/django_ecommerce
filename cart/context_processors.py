from cart.models import Cart, CartItem

def cart_count_processor(request):
    """Contexto global para contar los elementos del carrito."""
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.total_items()
        except Cart.DoesNotExist:
            cart_count = 0
    elif request.session.session_key:
        try:
            cart = Cart.objects.get(session__session_key=request.session.session_key)
            cart_count = cart.total_items()
        except Cart.DoesNotExist:
            cart_count = 0
    return {'cart_count': cart_count}
