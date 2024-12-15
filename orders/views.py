# Python  
from decimal import Decimal

# Terceros
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

# Local
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
                'address': profile.address if profile else '',
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


@login_required
def list_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'accounts/my_order_detail.html', {
        'order': order,
        'items': order.items.all()
    })


@require_http_methods(["GET"])
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    ordered_items = order.items.all()

    subtotal = sum(item.subtotal() for item in ordered_items)
    iva = subtotal * Decimal('0.19')
    total = subtotal + iva

    context = {
        'order': order,
        'ordered_products': ordered_items,
        'subtotal': subtotal,
        'order_tax': iva,
        'order_total': total
    }

    return render(request, 'orders/order_complete.html', context)

