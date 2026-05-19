# administracion/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponse

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)


from social.models import ComentarioProducto
from usuarios.models import *


User = get_user_model()


# =========================================
# VALIDAR ADMIN
# =========================================
def es_admin(user):

    return (

        user.is_superuser or
        user.is_staff or
        getattr(user, "is_admin_manual", False)
    )


# =========================================
# DASHBOARD
# =========================================
@login_required
@user_passes_test(es_admin)
def dashboard(request):

    total_usuarios = User.objects.count()

    usuarios_activos = User.objects.filter(
        is_active=True
    ).count()

    total_emprendimientos = Emprendimiento.objects.count()

    emprendimientos_revision = Emprendimiento.objects.filter(
        estado="revision"
    ).count()

    total_productos = Producto.objects.count()

    total_comentarios = ComentarioProducto.objects.count()

    total_chats = total_chats.objects.count()

    context = {

        "total_usuarios": total_usuarios,

        "usuarios_activos": usuarios_activos,

        "total_emprendimientos": total_emprendimientos,

        "emprendimientos_revision": emprendimientos_revision,

        "total_productos": total_productos,

        "total_comentarios": total_comentarios,

        "total_chats": total_chats,
    }

    return render(
        request,
        "administracion/dashboard.html",
        context
    )


# =========================================
# LISTA USUARIOS
# =========================================
@login_required
@user_passes_test(es_admin)
def lista_usuarios(request):

    usuarios = User.objects.all().order_by("-id")

    if request.method == "POST":

        user_id = request.POST.get("user_id")

        action = request.POST.get("action")

        try:

            usuario = User.objects.get(id=user_id)

        except User.DoesNotExist:

            messages.error(
                request,
                "Usuario no encontrado."
            )

            return redirect("lista_usuarios")

        # ELIMINAR
        if action == "delete":

            usuario.delete()

            messages.success(
                request,
                "Usuario eliminado."
            )

        # HACER ADMIN
        elif action == "make_admin":

            usuario.is_admin_manual = True
            usuario.is_staff = True

            usuario.save()

            messages.success(
                request,
                "Usuario convertido en administrador."
            )

        # QUITAR ADMIN
        elif action == "remove_admin":

            usuario.is_admin_manual = False
            usuario.is_staff = False

            usuario.save()

            messages.success(
                request,
                "Permisos removidos."
            )

        return redirect("lista_usuarios")

    return render(
        request,
        "administracion/usuarios_list.html",
        {
            "usuarios": usuarios
        }
    )


# =========================================
# SOLICITUDES EMPRENDIMIENTO
# =========================================
@login_required
@user_passes_test(es_admin)
def solicitudes(request):

    if request.method == "POST":

        action = request.POST.get("action")

        emp_id = request.POST.get("empr_id")

        try:

            emprendimiento = Emprendimiento.objects.get(
                id=emp_id
            )

        except Emprendimiento.DoesNotExist:

            messages.error(
                request,
                "Emprendimiento no encontrado."
            )

            return redirect("solicitudes")

        # APROBAR
        if action == "aprobar":

            emprendimiento.estado = "aprobado"

            emprendimiento.usuario.es_emprendedor = True

            emprendimiento.usuario.save()

            emprendimiento.save()

            Notificacion.objects.create(

                usuario=emprendimiento.usuario,

                mensaje=f"Tu emprendimiento '{emprendimiento.nombre}' fue aprobado.",

                tipo="aprobado"
            )

            messages.success(
                request,
                "Emprendimiento aprobado."
            )

        # RECHAZAR
        elif action == "rechazar":

            emprendimiento.estado = "rechazado"

            emprendimiento.save()

            Notificacion.objects.create(

                usuario=emprendimiento.usuario,

                mensaje=f"Tu emprendimiento '{emprendimiento.nombre}' fue rechazado.",

                tipo="rechazado"
            )

            messages.warning(
                request,
                "Emprendimiento rechazado."
            )

        return redirect("solicitudes")

    pendientes = Emprendimiento.objects.filter(
        estado="revision"
    ).order_by("-id")

    return render(
        request,
        "administracion/solicitudes.html",
        {
            "pendientes": pendientes
        }
    )


# =========================================
# PRODUCTOS
# =========================================
@login_required
@user_passes_test(es_admin)
def lista_productos(request):

    productos = Producto.objects.select_related(
        "emprendimiento"
    ).all()

    return render(

        request,

        "administracion/productos.html",

        {
            "productos": productos
        }
    )


# =========================================
# COMENTARIOS
# =========================================
@login_required
@user_passes_test(es_admin)
def lista_comentarios(request):

    comentarios = ComentarioProducto.objects.select_related(
        "usuario",
        "producto"
    ).all()

    return render(

        request,

        "administracion/comentarios.html",

        {
            "comentarios": comentarios
        }
    )


# =========================================
# CHATS
# =========================================
@login_required
@user_passes_test(es_admin)
def lista_chats(request):

    chats = chats.objects.select_related(
        "usuario",
        "emprendimiento"
    ).all()

    return render(

        request,

        "administracion/chats.html",

        {
            "chats": chats
        }
    )


# =========================================
# PDF EMPRENDIMIENTO
# =========================================
@login_required
@user_passes_test(es_admin)
def descargar_emprendimiento_pdf(request, emp_id):

    try:

        emp = Emprendimiento.objects.get(id=emp_id)

    except Emprendimiento.DoesNotExist:

        messages.error(
            request,
            "Emprendimiento no encontrado."
        )

        return redirect("solicitudes")

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="emprendimiento_{emp.id}.pdf"'

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    contenido = []

    contenido.append(

        Paragraph(
            "Solicitud de Emprendimiento",
            styles["Title"]
        )
    )

    contenido.append(Spacer(1, 20))

    contenido.append(

        Paragraph(
            f"<b>Nombre:</b> {emp.nombre}",
            styles["Normal"]
        )
    )

    contenido.append(

        Paragraph(
            f"<b>Descripción:</b> {emp.descripcion}",
            styles["Normal"]
        )
    )

    contenido.append(

        Paragraph(
            f"<b>Ciudad:</b> {emp.ciudad}",
            styles["Normal"]
        )
    )

    contenido.append(

        Paragraph(
            f"<b>Estado:</b> {emp.estado}",
            styles["Normal"]
        )
    )

    doc.build(contenido)

    return response