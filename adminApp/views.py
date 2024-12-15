# Python
import csv
from datetime import datetime

# Django
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

# Local
from accounts.models import Account, UserProfile
from category.models import Category
from inventory.models import Inventory, StockMovement
from orders.models import Order, OrderItem
from store.models import Product, ReviewRating


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
    PRODUCTOS E INVENTARIO
"""

# Vista combinada para listar productos e inventario
@method_decorator(user_passes_test(admin_required), name='dispatch')
class ProductInventoryListView(ListView):
    model = Product
    template_name = "adminApp/product_list.html"
    context_object_name = "product_inventory"

    def get_queryset(self):
        return Product.objects.select_related('inventory').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_url'] = reverse_lazy('adminApp:export_product_csv')
        return context


@user_passes_test(admin_required)
def export_product_csv(request):
    # Exportar datos combinados de productos e inventarios
    queryset = Product.objects.select_related('inventory').all()

    # Crear respuesta HTTP con contenido CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="product_inventory.csv"'

    # Crear escritor CSV
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nombre', 'Precio', 'Categoría', 'Disponible', 'Stock', 'Stock Mínimo'])

    for product in queryset:
        inventory = getattr(product, 'inventory', None)
        writer.writerow([
            product.id,
            product.product_name,
            product.price,
            product.category.category_name,
            'Sí' if product.is_available else 'No',
            inventory.stock if inventory else 'N/A',
            inventory.stock_minimum if inventory else 'N/A',
        ])

    return response


# Vista combinada para crear productos con inventario
@method_decorator(user_passes_test(admin_required), name='dispatch')
class ProductInventoryCreateView(CreateView):
    model = Product
    fields = ['product_name', 'slug', 'description', 'price', 'images', 'is_available', 'category']
    template_name = "adminApp/product_form.html"
    success_url = reverse_lazy('adminApp:product_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Crear inventario asociado automáticamente
        Inventory.objects.create(
            product=self.object,
            stock=self.request.POST.get('stock', 0),
            stock_minimum=self.request.POST.get('stock_minimum', 0),
        )
        return response


@method_decorator(user_passes_test(admin_required), name='dispatch')
class ProductInventoryUpdateView(UpdateView):
    model = Product
    fields = ['product_name', 'slug', 'description', 'price', 'images', 'is_available', 'category']
    template_name = "adminApp/product_form.html"
    success_url = reverse_lazy('adminApp:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inventory'] = getattr(self.object, 'inventory', None)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Actualizar inventario asociado
        inventory = self.object.inventory
        new_stock = int(self.request.POST.get('stock', inventory.stock))
        stock_minimum = int(self.request.POST.get('stock_minimum', inventory.stock_minimum))

        # Registrar movimiento
        if new_stock != inventory.stock:
            movement_type = 'entrada' if new_stock > inventory.stock else 'salida'
            quantity = abs(new_stock - inventory.stock)
            StockMovement.register_movement(
                inventory=inventory,
                movement_type=movement_type,
                quantity=quantity
            )

        # Actualizar inventario con los nuevos valores
        inventory.stock = new_stock
        inventory.stock_minimum = stock_minimum
        inventory.save()

        return response


# Vista para eliminar productos (y el inventario asociado automáticamente)
@method_decorator(user_passes_test(admin_required), name='dispatch')
class ProductInventoryDeleteView(DeleteView):
    model = Product
    template_name = "adminApp/product_confirm_delete.html"
    success_url = reverse_lazy('adminApp:product_list')


"""
    RESEÑAS DE PRODUCTO
"""
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
    MOVIMIENTOS DE INVENTARIO
"""

@method_decorator(user_passes_test(admin_required), name='dispatch')
class StockMovementListView(ListView):
    model = StockMovement
    template_name = "adminApp/stock_movement_list.html"
    context_object_name = "movements"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-movement_date')
        # Filtrar por tipo de movimiento
        movement_type = self.request.GET.get('movement_type')
        if movement_type in dict(StockMovement.MOVEMENT_CHOICES):
            queryset = queryset.filter(movement_type=movement_type)

        # Filtrar por rango de fechas
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(movement_date__range=[start_date, end_date])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movement_choices'] = StockMovement.MOVEMENT_CHOICES
        return context


@user_passes_test(admin_required)
def export_stock_movements_csv(request):
    queryset = StockMovement.objects.select_related('inventory', 'inventory__product')

    # Crear respuesta HTTP con tipo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stock_movements.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID Movimiento', 'Producto', 'Tipo', 'Cantidad', 'Fecha'])

    for movement in queryset:
        writer.writerow([
            movement.id,
            movement.inventory.product.product_name,
            movement.get_movement_type_display(),
            movement.quantity,
            movement.movement_date,
        ])

    return response


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
        queryset = queryset.order_by('-created_at')
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.STATUS_CHOICES  # Pasar los estados disponibles al contexto
        return context

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

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_staff=False).order_by('date_joined')
        return queryset

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

    def get_queryset(self):
        queryset = super().get_queryset().filter(user__is_staff=False).order_by('user__email')
        return queryset


# Actualizar Perfiles de Usuario
@method_decorator(user_passes_test(admin_required), name='dispatch')
class UserProfileUpdateView(UpdateView):
    model = UserProfile
    fields = ['rut', 'profile_picture', 'address', 'phone_number', 'additional_data']
    template_name = "adminApp/userprofile_form.html"
    success_url = reverse_lazy('adminApp:userprofile_list')


"""
    Gráficos
"""


def sales_chart_view(request):
    return render(request, 'adminApp/sales_chart.html')


def sales_data_api(request):
    # Filtrar las órdenes completadas
    completed_orders = Order.objects.filter(status='completed')

    # Filtros dinámicos
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    product_ids = request.GET.getlist('product_ids')

    if start_date:
        completed_orders = completed_orders.filter(created_at__gte=start_date)
    if end_date:
        completed_orders = completed_orders.filter(created_at__lte=end_date)

    # Filtrar por productos si se especifican
    order_items = OrderItem.objects.filter(order__in=completed_orders)
    if product_ids:
        order_items = order_items.filter(product_id__in=product_ids)

    # Agrupar y sumar los subtotales por producto
    sales_data = order_items.values('product__product_name').annotate(
        total_sales=Sum(F('quantity') * F('price'))
    ).order_by('-total_sales')

    return JsonResponse(list(sales_data), safe=False)


def stock_movements_chart_view(request):
    return render(request, 'adminApp/stock_movements_chart.html')

def stock_movements_data_api(request):

    # Filtrar por rango de fechas
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    movements = StockMovement.objects.select_related('inventory', 'inventory__product')

    if start_date:
        movements = movements.filter(movement_date__gte=start_date)
    if end_date:
        movements = movements.filter(movement_date__lte=end_date)

    # Agrupar por producto y tipo de movimiento, sumar cantidades
    stock_data = movements.values(
        'inventory__product__product_name',  # Nombre del producto
        'movement_type'  # Tipo de movimiento (entrada/salida)
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('inventory__product__product_name', 'movement_type')

    return JsonResponse(list(stock_data), safe=False)

