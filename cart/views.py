# Django
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages

# Local
from .models import get_or_create_cart, add_to_cart, update_cart_item, remove_from_cart, CartItem, CartError, StockError
from store.models import Product


@require_http_methods(["GET"])
def view_cart(request):
    """
    Devuelve el contenido del carrito actual como JSON.
    """
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
    """
    Agrega un producto al carrito.
    """
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        messages.error(request, "Cantidad inválida.")
        return redirect(product.get_url())

    try:
        add_to_cart(cart, product, quantity)
        messages.success(request, f"¡'{product.product_name}' ha sido agregado al carrito!")
    except StockError:
        messages.error(request, "No hay suficiente stock para este producto.")
    except CartError as e:
        messages.error(request, str(e))

    return redirect(product.get_url())


@require_http_methods(["POST", "PATCH"])
def update_cart_item_view(request, cart_item_id):
    """
    Actualiza la cantidad de un ítem en el carrito.
    """
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    try:
        quantity = int(request.POST.get("quantity", 0))
        update_cart_item(cart_item, quantity)
        # Redirige de vuelta a la página del carrito
        return redirect('cart_page')
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["POST"])
def delete_cart_item_view(request, cart_item_id):
    """
    Elimina un ítem del carrito y redirige a la página del carrito.
    """
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    try:
        remove_from_cart(cart_item)
        return redirect('cart_page')  # Redirige de vuelta al carrito
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def cart_page(request):
    """
    Renderiza una página HTML con el contenido del carrito.
    """
    cart = get_or_create_cart(request)
    cart_items = cart.cartitems.all()
    total = cart.total_cost()
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/cart.html', context)
