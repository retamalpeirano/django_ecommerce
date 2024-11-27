from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Product, ReviewRating
from category.models import Category
from inventory.models import Inventory
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages


def store(request, category_slug=None):
    """
    Muestra productos por categoría o todos los productos si no se especifica una categoría.
    Adicionalmente permite filtrar por rango de precios.
    """
    categories = None
    products = Product.objects.filter(is_available=True)  # Inicializamos los productos disponibles

    # Filtrar por categoría si se pasa en la URL
    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=categories)

    # Filtrar por rango de precios si los parámetros están presentes
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    # Paginación
    paginator = Paginator(products, 6)  # Mostrar 6 productos por página
    page = request.GET.get('page')
    try:
        paged_products = paginator.page(page)
    except PageNotAnInteger:
        paged_products = paginator.page(1)
    except EmptyPage:
        paged_products = paginator.page(paginator.num_pages)

    context = {
        'products': paged_products,
        'product_count': products.count(),  # Número total de productos después del filtrado
        'categories': categories,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    """
    Muestra los detalles de un producto específico.
    """
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        inventory = Inventory.objects.filter(product=single_product).first()
    except Product.DoesNotExist:
        single_product = None
        inventory = None

    reviews = ReviewRating.objects.filter(product=single_product, status=True)

    review_form = ReviewForm()
    context = {
        'single_product': single_product,
        'inventory': inventory,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    """
    Permite buscar productos según palabras clave.
    """
    products = None
    query = request.GET.get('keyword')
    if query:
        products = Product.objects.filter(
            Q(product_name__icontains=query) | Q(description__icontains=query), is_available=True
        )

    context = {
        'products': products,
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    """
    Permite que los usuarios dejen reseñas en los productos. Si ya existe una reseña del usuario para el producto,
    la actualiza. Si no, crea una nueva.
    """
    url = request.META.get('HTTP_REFERER', '/')
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        try:
            # Intentar recuperar una reseña existente
            existing_review = ReviewRating.objects.get(user=request.user, product=product)
            form = ReviewForm(request.POST, instance=existing_review)
            if form.is_valid():
                form.save()
                messages.success(request, '¡Tu comentario ha sido actualizado con éxito!')
        except ReviewRating.DoesNotExist:
            # Crear una nueva reseña
            form = ReviewForm(request.POST)
            if form.is_valid():
                new_review = form.save(commit=False)
                new_review.product = product
                new_review.user = request.user
                new_review.ip = request.META.get('REMOTE_ADDR', '')
                new_review.save()
                messages.success(request, '¡Gracias por tu comentario!')
    
    return redirect(url)


def add_cart(request, product_id):
    # Aquí va la lógica para agregar el producto al carrito.
    # Como ejemplo básico, redirigiremos a la tienda.
    return redirect('store')
