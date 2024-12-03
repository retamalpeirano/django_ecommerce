from django.urls import path
from . import views

# app_name = 'adminApp'

urlpatterns = [
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Categorías
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Productos
    #path('products/', views.ProductListView.as_view(), name='product_list'),
    #path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    #path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    #path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Inventario
    #path('inventory/', views.InventoryListView.as_view(), name='inventory_list'),
]