from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('list/', views.list_orders, name='list_orders'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
]
