from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from category.models import Category
from store.models import Product, ReviewRating
from inventory.models import Inventory, StockMovement

# Restricción para usuarios administradores
def admin_required(user):
    return user.is_authenticated and user.is_staff

# Vista del dashboard
@method_decorator(user_passes_test(admin_required), name='dispatch')
class DashboardView(TemplateView):
    template_name = "adminApp/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_count'] = Category.objects.count()
        return context

"""
    CATEGORÍAS
"""

# Listar Categorías
@method_decorator(user_passes_test(admin_required), name='dispatch')
class CategoryListView(ListView):
    model = Category
    template_name = "adminApp/category_list.html"
    context_object_name = "categories"

# Crear Categoría
@method_decorator(user_passes_test(admin_required), name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    fields = ['category_name', 'description', 'cat_image']
    template_name = "adminApp/category_form.html"
    success_url = reverse_lazy('adminApp:category_list')

# Actualizar Categoría
@method_decorator(user_passes_test(admin_required), name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['category_name', 'description', 'cat_image']
    template_name = "adminApp/category_form.html"
    success_url = reverse_lazy('adminApp:category_list')

# Eliminar Categoría
@method_decorator(user_passes_test(admin_required), name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = "adminApp/category_confirm_delete.html"
    success_url = reverse_lazy('adminApp:category_list')

"""
    PRODUCTOS Y REVIEWS
"""

# Listar Productos
@method_decorator(user_passes_test(admin_required), name='dispatch')
class ProductListView(ListView):
    model = Product
    template_name = "adminApp/product_list.html"
    context_object_name = "products"

# Crear Productos
@method_decorator(user_passes_test(admin_required), name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    fields = ['product_name', 'slug', 'description', 'price', 'images', 'is_available', 'category']
    template_name = "adminApp/product_form.html"
    success_url = reverse_lazy('adminApp:product_list')

# Actualizar Productos
@method_decorator(user_passes_test(admin_required), name='dispatch')
class ProductUpdateView(UpdateView):
    model = Product
    fields = ['product_name', 'slug', 'description', 'price', 'images', 'is_available', 'category']
    template_name = "adminApp/product_form.html"
    success_url = reverse_lazy('adminApp:product_list')

# Eliminar Productos
@method_decorator(user_passes_test(admin_required), name='dispatch')
class ProductDeleteView(DeleteView):
    model = Product
    template_name = "adminApp/product_confirm_delete.html"
    success_url = reverse_lazy('adminApp:product_list')


# Listar Reviews
@method_decorator(user_passes_test(admin_required), name='dispatch')
class ReviewRatingListView(ListView):
    model = ReviewRating
    template_name = "adminApp/reviewrating_list.html"
    context_object_name = "reviews"

# Eliminar Reviews
@method_decorator(user_passes_test(admin_required), name='dispatch')
class ReviewRatingDeleteView(DeleteView):
    model = ReviewRating
    template_name = "adminApp/reviewrating_confirm_delete.html"
    success_url = reverse_lazy('adminApp:reviewrating_list')
    
"""
    INVENTARIO
"""
@method_decorator(user_passes_test(admin_required), name='dispatch')
class InventoryListView(ListView):
    model = Inventory
    template_name = "adminApp/inventory_list.html"
    context_object_name = "inventories"

@method_decorator(user_passes_test(admin_required), name='dispatch')
class InventoryCreateView(CreateView):
    model = Inventory
    fields = ['product', 'stock', 'stock_minimum']
    template_name = "adminApp/inventory_form.html"
    success_url = reverse_lazy('adminApp:inventory_list')

    def form_valid(self, form):
        # Registrar movimiento al crear un inventario
        response = super().form_valid(form)
        StockMovement.register_movement(
            inventory=self.object,
            movement_type='entrada',
            quantity=self.object.stock
        )
        return response

@method_decorator(user_passes_test(admin_required), name='dispatch')
class InventoryUpdateView(UpdateView):
    model = Inventory
    fields = ['product', 'stock', 'stock_minimum']
    template_name = "adminApp/inventory_form.html"
    success_url = reverse_lazy('adminApp:inventory_list')

    def form_valid(self, form):
        # Registrar movimiento al actualizar el inventario
        inventory = self.get_object()
        new_stock = form.cleaned_data['stock']
        movement_type = 'entrada' if new_stock > inventory.stock else 'salida'
        quantity = abs(new_stock - inventory.stock)
        StockMovement.register_movement(
            inventory=inventory,
            movement_type=movement_type,
            quantity=quantity
        )
        return super().form_valid(form)

@method_decorator(user_passes_test(admin_required), name='dispatch')
class InventoryDeleteView(DeleteView):
    model = Inventory
    template_name = "adminApp/inventory_confirm_delete.html"
    success_url = reverse_lazy('adminApp:inventory_list')

    def delete(self, request, *args, **kwargs):
        inventory = self.get_object()
        StockMovement.register_movement(
            inventory=inventory,
            movement_type='salida',
            quantity=inventory.stock
        )
        return super().delete(request, *args, **kwargs)