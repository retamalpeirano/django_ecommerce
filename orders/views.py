from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db import transaction
from accounts.models import Account, UserProfile
from cart.models import get_or_create_cart
from .models import Order




@transaction.atomic
@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = get_or_create_cart(request)
    if not cart.cartitems.exists():
        return redirect('cart_page')  # Redirigir si el carrito está vacío

    if request.method == "GET":
        # Autocompletar datos si el usuario está autenticado
        if request.user.is_authenticated:
            user = request.user
            profile = user.profile if hasattr(user, 'profile') else None
            initial_data = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': profile.phone_number if profile else '',
                'address_line_1': profile.address.get('line1', '') if profile and profile.address else '',
                'address_line_2': profile.address.get('line2', '') if profile and profile.address else '',
                'city': profile.address.get('city', '') if profile and profile.address else '',
                'state': profile.address.get('state', '') if profile and profile.address else '',
                'country': profile.address.get('country', '') if profile and profile.address else '',
                'rut': profile.rut if profile else '',
            }
        else:
            initial_data = {}
        return render(request, 'store/checkout.html', {'cart': cart, 'cart_items': cart.cartitems.all(), 'total': cart.total_cost(), 'initial_data': initial_data})

    # Procesar POST para crear la orden
    form_data = request.POST
    if request.user.is_authenticated:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created or not profile.rut:
            profile.rut = form_data.get('rut', '')
        if not user.first_name or not user.last_name:
            user.first_name = form_data.get('first_name', user.first_name)
            user.last_name = form_data.get('last_name', user.last_name)
            user.save()

        profile.phone_number = form_data.get('phone', profile.phone_number)
        profile.address = form_data.get('address', profile.address)
        profile.save()
    else:
        # Crear cuenta y perfil para un usuario anónimo
        email = form_data.get('email')
        user = Account.objects.create(email=email, username=email.split('@')[0], is_active=False)
        user.set_unusable_password()
        user.first_name = form_data.get('first_name', '')
        user.last_name = form_data.get('last_name', '')
        user.save()

        UserProfile.objects.create(
            user=user,
            rut=form_data.get('rut', ''),
            phone_number=form_data.get('phone', ''),
            address=form_data.get('address', ''),
        )

    # Validar stock antes de crear la orden
    for cart_item in cart.cartitems.all():
        product = cart_item.product
        inventory = product.inventory
        if inventory and inventory.stock < cart_item.quantity:
            return render(request, 'store/checkout.html', {
                'cart': cart,
                'cart_items': cart.cartitems.all(),
                'total': cart.total_cost(),
                'error': f"No hay suficiente stock para el producto {product.product_name}."
            })

    try:
        order = Order.create_from_cart(cart, user=user, status='completed')
    except ValueError as e:
        return render(request, 'store/checkout.html', {
            'cart': cart,
            'cart_items': cart.cartitems.all(),
            'total': cart.total_cost(),
            'error': str(e)
        })
    except Exception as e:
        return render(request, 'store/checkout.html', {
            'cart': cart,
            'cart_items': cart.cartitems.all(),
            'total': cart.total_cost(),
            'error': "Ocurrió un error inesperado al procesar su pedido. Intente nuevamente."
        })

    return redirect('order_success', order_id=order.id)


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
