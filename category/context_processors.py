"""
    PROCESADOR DE CONTENIDO CATEGORÍAS
"""

from .models import Category

def menu_links(request):
    links = Category.objects.all()  # Puedes optimizar esta consulta en el futuro si es necesario
    return {'links': links}
