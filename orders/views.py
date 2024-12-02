from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from cart.models import get_or_create_cart
from .models import Order


@require_http_methods(["POST"])
def create_order(request):
    """Convierte el carrito actual en una orden."""
    cart = get_or_create_cart(request)
    user = request.user if request.user.is_authenticated else None

    # Verificar si el carrito está vacío
    if not cart.cartitems.exists():
        return JsonResponse({"error": "El carrito está vacío."}, status=400)

    # Verificar si ya existe una orden pendiente para este carrito
    #if Order.objects.filter(user=user, session=cart.session, status='pending').exists():
    #    return JsonResponse({"error": "Ya existe una orden pendiente para este carrito."}, status=400)

    try:
        # Crear la orden usando el método del modelo Order
        order = Order.create_from_cart(cart, user=user, session=cart.session)
        return JsonResponse({
            "message": "Orden creada exitosamente.",
            "order_id": order.id,
            "total_price": order.total_price,
            "status": order.get_status_display(),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)



@require_http_methods(["GET"])
def list_orders(request):
    """Lista las órdenes del usuario autenticado."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Debe estar autenticado para ver sus órdenes."}, status=403)

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    data = [
        {
            "id": order.id,
            "total_price": order.total_price,
            "status": order.get_status_display(),
            "created_at": order.created_at,
        }
        for order in orders
    ]
    return JsonResponse({"orders": data})


@require_http_methods(["GET"])
def order_detail(request, order_id):
    """Devuelve los detalles de una orden específica."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    items = [
        {
            "product_name": item.product.product_name,
            "quantity": item.quantity,
            "price": item.price,
            "subtotal": item.subtotal(),
        }
        for item in order.items.all()
    ]
    return JsonResponse({
        "order_id": order.id,
        "total_price": order.total_price,
        "status": order.get_status_display(),
        "items": items,
    })
