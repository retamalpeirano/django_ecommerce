from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from accounts.models import Account, UserProfile
from category.models import Category
from store.models import Product, ReviewRating
from inventory.models import Inventory, StockMovement
from orders.models import Order, OrderItem
import csv


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
        context['low_stock_alerts'] = [
            inventory.stock_minimun_message() for inventory in Inventory.objects.all() if inventory.almost_out()
        ]
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
    fields = ['category_name', 'description']
    template_name = "adminApp/category_form.html"
    success_url = reverse_lazy('adminApp:category_list')


# Actualizar Categoría
@method_decorator(user_passes_test(admin_required), name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['category_name', 'description']
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
    

"""
    ORDENES
"""

@method_decorator(user_passes_test(admin_required), name='dispatch')
class OrderListView(ListView):
    model = Order
    template_name = "adminApp/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por usuario
        user_filter = self.request.GET.get('user')
        if user_filter:
            queryset = queryset.filter(user__id=user_filter)

        # Filtrar por estado
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filtrar por rango de fechas
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        return queryset

    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        if order_id and new_status in dict(Order.STATUS_CHOICES):
            try:
                order = Order.objects.get(id=order_id)
                order.status = new_status
                order.save()
            except Order.DoesNotExist:
                pass
        return redirect('adminApp:order_list')


@user_passes_test(admin_required)
def export_orders_csv(request):
    queryset = Order.objects.all()

    # Filtrar según parámetros GET
    user_filter = request.GET.get('user')
    if user_filter:
        queryset = queryset.filter(user__id=user_filter)
    status_filter = request.GET.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        queryset = queryset.filter(created_at__range=[start_date, end_date])

    # Crear CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Usuario', 'Estado', 'Precio Total', 'Fecha de Creación', 'Última Actualización'])
    for order in queryset:
        writer.writerow([
            order.id,
            order.user.email if order.user else "Anónimo",
            order.get_status_display(),
            order.total_price,
            order.created_at,
            order.updated_at,
        ])

    return response


"""
    DETALLE ORDENES
"""

@method_decorator(user_passes_test(admin_required), name='dispatch')
class OrderItemListView(ListView):
    model = OrderItem
    template_name = "adminApp/order_detail_list.html"
    context_object_name = "order_items"
    paginate_by = 10

    def get_queryset(self):
        # Obtener los items de una orden específica
        order_id = self.kwargs.get('order_id')
        return OrderItem.objects.filter(order_id=order_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        context['order'] = Order.objects.filter(id=order_id).first()
        return context


@user_passes_test(admin_required)
def export_order_items_csv(request, order_id):
    items = OrderItem.objects.filter(order_id=order_id)

    # Crear CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="order_{order_id}_items.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID Orden', 'Producto', 'Cantidad', 'Precio Unitario', 'Subtotal'])
    for item in items:
        writer.writerow([
            item.order.id,
            item.product.product_name,
            item.quantity,
            item.price,
            item.subtotal()
        ])

    return response


""" 
    CUENTAS Y PERFILES
"""

# Listar Cuentas
@method_decorator(user_passes_test(admin_required), name='dispatch')
class AccountListView(ListView):
    model = Account
    template_name = "adminApp/account_list.html"
    context_object_name = "accounts"
    paginate_by = 10


# Actualizar Cuentas
@method_decorator(user_passes_test(admin_required), name='dispatch')
class AccountUpdateView(UpdateView):
    model = Account
    fields = ['email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'is_customer']
    template_name = "adminApp/account_form.html"
    success_url = reverse_lazy('adminApp:account_list')


# Listar Perfiles de Usuario
@method_decorator(user_passes_test(admin_required), name='dispatch')
class UserProfileListView(ListView):
    model = UserProfile
    template_name = "adminApp/userprofile_list.html"
    context_object_name = "user_profiles"
    paginate_by = 10


# Actualizar Perfiles de Usuario
@method_decorator(user_passes_test(admin_required), name='dispatch')
class UserProfileUpdateView(UpdateView):
    model = UserProfile
    fields = ['rut', 'profile_picture', 'address', 'phone_number', 'additional_data']
    template_name = "adminApp/userprofile_form.html"
    success_url = reverse_lazy('adminApp:userprofile_list')