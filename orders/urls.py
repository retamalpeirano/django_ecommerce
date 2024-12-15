from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('my_orders/', views.list_orders, name='my_orders'),
    path('detail/<int:order_id>/', views.order_detail, name='my_order_detail'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
]
