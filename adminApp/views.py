from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from category.models import Category

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
