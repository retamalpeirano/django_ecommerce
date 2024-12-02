from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import get_or_create_cart, add_to_cart, update_cart_item, remove_from_cart, CartItem
from store.models import Product

@require_http_methods(["GET"])
def view_cart(request):
    """Devuelve el contenido del carrito actual."""
    cart = get_or_create_cart(request)
    items = [
        {
            "product_name": item.product.product_name,
            "quantity": item.quantity,
            "price": item.product.price,
            "subtotal": item.subtotal(),
        }
        for item in cart.cartitems.all()
    ]
    return JsonResponse({
        "items": items,
        "total_items": cart.total_items(),
        "total_cost": cart.total_cost(),
    })


@require_http_methods(["POST"])
def add_product_to_cart(request, product_id):
    """Agrega un producto al carrito."""
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)

    try:
        quantity = int(request.POST.get("quantity", 1))
        cart_item = add_to_cart(cart, product, quantity)
        return JsonResponse({
            "message": "Producto agregado exitosamente.",
            "product_name": cart_item.product.product_name,
            "quantity": cart_item.quantity,
            "subtotal": cart_item.subtotal(),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["PUT", "PATCH"])
def update_cart_item_view(request, cart_item_id):
    """Actualiza la cantidad de un ítem en el carrito."""
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    try:
        quantity = int(request.POST.get("quantity", 0))
        update_cart_item(cart_item, quantity)
        return JsonResponse({
            "message": "Cantidad actualizada correctamente.",
            "product_name": cart_item.product.product_name,
            "quantity": cart_item.quantity,
            "subtotal": cart_item.subtotal(),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["DELETE"])
def delete_cart_item_view(request, cart_item_id):
    """Elimina un ítem del carrito."""
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    try:
        remove_from_cart(cart_item)
        return JsonResponse({"message": "Producto eliminado del carrito."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
