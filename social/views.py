from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from usuarios.models import *
from .models import *
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

@login_required
@require_POST
def toggle_seguimiento(request, emprendimiento_id):

    emprendimiento = get_object_or_404(
        Emprendimiento,
        id=emprendimiento_id
    )

    seguimiento = Seguimiento.objects.filter(
        usuario=request.user,
        emprendimiento=emprendimiento
    ).first()

    if seguimiento:
        seguimiento.delete()
        siguiendo = False
    else:
        Seguimiento.objects.create(
            usuario=request.user,
            emprendimiento=emprendimiento
        )
        siguiendo = True

    total_seguidores = Seguimiento.objects.filter(
        emprendimiento=emprendimiento
    ).count()

    # Si es AJAX
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "siguiendo": siguiendo,
            "total_seguidores": total_seguidores
        })

    # Si viene de un form normal
    return redirect("ver_emprendimiento", id=emprendimiento.id)


@login_required
@require_POST
def crear_solicitud_contacto(request, producto_id):

    producto = get_object_or_404(
        Producto,
        id=producto_id
    )

    tipo = request.POST.get("tipo")
    mensaje = request.POST.get("mensaje", "").strip()

    SolicitudContacto.objects.create(
        usuario=request.user,
        emprendimiento=producto.emprendimiento,
        producto=producto,
        tipo=tipo,
        mensaje=mensaje
    )

    messages.success(
        request,
        "Tu solicitud fue enviada al vendedor."
    )

    return redirect("ver_producto", id=producto.id)




@login_required
def contacto_producto(request, producto_id):

    producto = get_object_or_404(Producto, id=producto_id)

    tipo_preseleccionado = request.GET.get("tipo", "")

    if request.method == "POST":

        tipo = request.POST.get("tipo")
        mensaje = request.POST.get("mensaje", "")

        ticket = SolicitudContacto.objects.create(
            usuario=request.user,
            producto=producto,
            emprendimiento=producto.emprendimiento,
            tipo=tipo,
            mensaje=mensaje,
            estado="pendiente"
        )

        # Notificación al emprendedor
        Notificacion.objects.create(
            usuario=producto.emprendimiento.usuario,
            mensaje=(
                f"{request.user.username} ha enviado una solicitud "
                f"de tipo '{ticket.get_tipo_display()}' "
                f"para el producto '{producto.nombre}'."
            ),
            tipo="contacto"
        )

        messages.success(
            request,
            "Tu solicitud fue enviada correctamente."
        )

        return redirect("contacto_producto", producto_id=producto.id)

    return render(
        request,
        "social/contacto_producto.html",
        {
            "producto": producto,
            "tipo_preseleccionado": tipo_preseleccionado,
        }
    )