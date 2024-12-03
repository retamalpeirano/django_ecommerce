from django.urls import path
from . import views
from cart.views import cart_page  # Importa la vista desde la aplicación "cart"

urlpatterns = [
    path('', views.store, name="store"),  # Página principal de la tienda
    path('category/<slug:category_slug>/', views.store, name="products_by_category"),  # Productos por categoría
    path('product/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),  # Detalles del producto
    path('search/', views.search, name='search'),  # Búsqueda
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),  # Reviews
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),  # Agregar al carrito
    path('cart/', cart_page, name='cart'),  # Página del carrito
]
