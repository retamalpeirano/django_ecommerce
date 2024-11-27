from django.shortcuts import render
from store.models import Product, ReviewRating

def home(request):
    products = Product.objects.filter(is_available=True).order_by('created_date')
    product_reviews = []

    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
        product_reviews.append({
            'product': product,
            'reviews': reviews,
        })

    context = {
        'product_reviews': product_reviews,
    }

    return render(request, 'home.html', context)


def dashboard(request):
    # Puedes agregar lógica personalizada aquí
    return render(request, 'accounts/dashboard.html')  # Asegúrate de que la plantilla `dashboard.html` exista