from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from cart.models import get_or_create_cart
from .models import Order
import logging



@require_http_methods(["GET", "POST"])
def checkout(request):
    """
    Renderiza la página de checkout (GET) y procesa la orden (POST).
    """
    cart = get_or_create_cart(request)

    if request.method == "POST":
        # Procesar la creación de la orden
        user = request.user if request.user.is_authenticated else None

        if not cart.cartitems.exists():
            return redirect('cart_page')  # Si el carrito está vacío, redirigir al carrito

        try:
            # Crear la orden usando el método del modelo Order
            order = Order.create_from_cart(cart, user=user, session=cart.session)
            return redirect('order_success', order_id=order.id)  # Redirigir a página de éxito
        except Exception as e:
            return render(request, 'store/checkout.html', {
                'cart': cart,
                'cart_items': cart.cartitems.all(),
                'total': cart.total_cost(),
                'error': str(e)
            })

    # Si es una solicitud GET, renderizar la página de checkout
    if not cart.cartitems.exists():
        return redirect('cart_page')  # Si el carrito está vacío, redirigir al carrito

    context = {
        'cart': cart,
        'cart_items': cart.cartitems.all(),
        'total': cart.total_cost(),
    }
    return render(request, 'store/checkout.html', context)


@require_http_methods(["POST"])
def create_order(request):
    """Convierte el carrito actual en una orden."""
    cart = get_or_create_cart(request)
    user = request.user if request.user.is_authenticated else None

    # Verificar si el carrito está vacío
    if not cart.cartitems.exists():
        return JsonResponse({"error": "El carrito está vacío."}, status=400)

    # Verificar si ya existe una orden pendiente para este carrito
    if Order.objects.filter(user=user, session=cart.session, status='pending').exists():
        return JsonResponse({"error": "Ya existe una orden pendiente para este carrito."}, status=400)

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
        return JsonResponse({"error": str(e)},status=400)


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


@require_http_methods(["GET"])
def order_success(request, order_id):
    """
    Renderiza una página de éxito después de la creación de una orden.
    """
    context = {
        'order_id': order_id
    }
    return render(request, 'store/order_success.html', context)
