from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_page, name='cart_page'),  # Página del carrito
    path('add/<int:product_id>/', views.add_product_to_cart, name='add_product_to_cart'),  # Agregar producto al carrito
    path('update/<int:cart_item_id>/', views.update_cart_item_view, name='update_cart_item'),  # Actualizar cantidad
    path('delete/<int:cart_item_id>/', views.delete_cart_item_view, name='delete_cart_item'),  # Eliminar ítem
]
