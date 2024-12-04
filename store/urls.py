from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),  # Página principal de la tienda
    path('category/<slug:category_slug>/', views.store, name="products_by_category"),  # Productos por categoría
    path('product/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),  # Detalles del producto
    path('search/', views.search, name='search'),  # Búsqueda
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),  # Reviews
]
