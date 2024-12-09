from django.urls import path
from . import views
from .views import (
    export_stock_movements_csv,
    StockMovementListView,
    export_product_csv,
    ProductInventoryListView,
    ProductInventoryCreateView,
    ProductInventoryUpdateView,
    ProductInventoryDeleteView,
    
)

app_name = 'adminApp'

urlpatterns = [
    
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Categorías
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Productos y Stock
    path('product-inventory/', ProductInventoryListView.as_view(), name='product_list'),
    path('product-inventory/create/', ProductInventoryCreateView.as_view(), name='product_create'),
    path('product-inventory/update/<int:pk>/', ProductInventoryUpdateView.as_view(), name='product_update'),
    path('product-inventory/delete/<int:pk>/', ProductInventoryDeleteView.as_view(), name='product_delete'),
    path('product-inventory/export/', export_product_csv, name='export_product_csv'),

    # Reviews
    path('reviews/', views.ReviewRatingListView.as_view(), name='reviewrating_list'),
    path('reviews/<int:pk>/delete/', views.ReviewRatingDeleteView.as_view(), name='reviewrating_delete'),

    # Movimientos de stock
    path('stock_movements/', StockMovementListView.as_view(), name='stock_movement_list'),
    path('stock_movements/export/', export_stock_movements_csv, name='export_stock_movements_csv'),

    # Ordenes y detalles de orden
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/export-csv/', views.export_orders_csv, name='export_orders_csv'),
    path('orders/<int:order_id>/items/', views.OrderItemListView.as_view(), name='order_items_list'),
    path('orders/<int:order_id>/items/export-csv/', views.export_order_items_csv, name='export_order_items_csv'),

    # Cuentas de usuario y perfiles de usuario
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/<int:pk>/update/', views.AccountUpdateView.as_view(), name='account_update'),
    path('userprofiles/', views.UserProfileListView.as_view(), name='userprofile_list'),
    path('userprofiles/<int:pk>/update/', views.UserProfileUpdateView.as_view(), name='userprofile_update'),

    # Gráficos
    path('grafics/sales-chart/', views.sales_chart_view, name='sales_chart'),
    path('grafics/stock-movements-chart/', views.stock_movements_chart_view, name='stock_movements_chart'),

    # Api
    path('api/sales-data/', views.sales_data_api, name='sales_data_api'),
    path('api/stock-movements-data/', views.stock_movements_data_api, name='stock_movements_data_api'),
]