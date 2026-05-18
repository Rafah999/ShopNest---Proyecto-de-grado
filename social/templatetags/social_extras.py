from django import template
from usuarios.models import Producto

register = template.Library()


@register.filter
def producto_por_id(producto_id):
    try:
        return Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return None