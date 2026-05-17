from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from usuarios.models import *
User = get_user_model()


def es_admin(user):
    return (
        user.is_superuser or
        user.is_staff or
        getattr(user, "is_admin_manual", False)
    )


@login_required
@user_passes_test(es_admin)
def dashboard(request):
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(
        is_active=True
    ).count()

    return render(
        request,
        "administracion/dashboard.html",
        {
            "total_usuarios": total_usuarios,
            "usuarios_activos": usuarios_activos,
        }
    )


@login_required
@user_passes_test(es_admin)
def usuarios_list(request):
    usuarios = User.objects.all().order_by("id")

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")

        if not user_id or not action:
            messages.error(
                request,
                "Solicitud inválida."
            )
            return redirect("usuarios_list")

        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(
                request,
                "Usuario no encontrado."
            )
            return redirect("usuarios_list")

        if (
            target.id == request.user.id and
            action in ("delete", "remove_admin")
        ):
            messages.error(
                request,
                "No puedes realizar esa acción sobre tu propia cuenta."
            )
            return redirect("usuarios_list")

        if action == "delete":
            target.delete()
            messages.success(
                request,
                f"Usuario {target.username} eliminado."
            )

        elif action == "make_admin":
            target.is_staff = True
            target.is_superuser = True
            target.save()

            messages.success(
                request,
                f"Usuario {target.username} promovido a administrador."
            )

        elif action == "remove_admin":
            target.is_staff = False
            target.is_superuser = False
            target.save()

            messages.success(
                request,
                f"Permisos de administrador removidos para {target.username}."
            )

        else:
            messages.error(
                request,
                "Acción desconocida."
            )

        return redirect("usuarios_list")

    return render(
        request,
        "administracion/usuarios_list.html",
        {
            "usuarios": usuarios
        }
    )


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
    content = []

    content.append(
        Paragraph(
            "Solicitud de Emprendimiento",
            styles["Title"]
        )
    )
    content.append(Spacer(1, 15))

    content.append(
        Paragraph(
            "<b>Datos del Emprendedor</b>",
            styles["Heading2"]
        )
    )
    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"Nombre: {emp.nombre_emprendedor} {emp.apellidos}",
            styles["Normal"]
        )
    )
    content.append(
        Paragraph(
            f"Documento: {emp.tipo_documento} - {emp.numero_documento}",
            styles["Normal"]
        )
    )
    content.append(
        Paragraph(
            f"Fecha nacimiento: {emp.fecha_nacimiento}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 15))

    content.append(
        Paragraph(
            "<b>Información del Emprendimiento</b>",
            styles["Heading2"]
        )
    )
    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"Nombre: {emp.nombre}",
            styles["Normal"]
        )
    )
    content.append(
        Paragraph(
            f"Descripción: {emp.descripcion}",
            styles["Normal"]
        )
    )
    content.append(
        Paragraph(
            f"Ubicación: {emp.ubicacion}",
            styles["Normal"]
        )
    )
    content.append(
        Paragraph(
            f"Ciudad: {emp.ciudad}",
            styles["Normal"]
        )
    )

    doc.build(content)

    return response



def es_admin(user):
    return (
        user.is_superuser or
        user.is_staff or
        getattr(user, "is_admin_manual", False)
    )


# =========================
# DASHBOARD
# =========================
@login_required
@user_passes_test(es_admin)
def dashboard(request):
    return render(request, "administracion/dashboard.html")


# =========================
# LISTA DE USUARIOS
# =========================
@login_required
@user_passes_test(es_admin)
def lista_usuarios(request):
    usuarios = User.objects.all().order_by("id")

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")

        try:
            user = User.objects.get(id=user_id)

            if action == "delete":
                user.delete()

            elif action == "make_admin":
                user.is_admin_manual = True
                user.is_staff = True
                user.save()

            elif action == "remove_admin":
                user.is_admin_manual = False
                user.is_staff = False
                user.save()

        except User.DoesNotExist:
            pass

        return redirect("lista_usuarios")

    return render(
        request,
        "administracion/usuarios_list.html",
        {"usuarios": usuarios}
    )


# =========================
# SOLICITUDES
# =========================
@login_required
@user_passes_test(es_admin)
def solicitudes(request):
    if request.method == "POST":
        action = request.POST.get("action")
        emp_id = request.POST.get("empr_id")

        try:
            e = Emprendimiento.objects.get(id=emp_id)

            if action == "aprobar":
                e.estado = "aprobado"

                Notificacion.objects.create(
                    usuario=e.usuario,
                    mensaje=f"¡Tu emprendimiento '{e.nombre}' ha sido aprobado!",
                    tipo="aprobado"
                )

                e.usuario.es_emprendedor = True
                e.usuario.save()
                e.save()

            elif action == "rechazar":
                e.estado = "rechazado"
                e.save()

                Notificacion.objects.create(
                    usuario=e.usuario,
                    mensaje=f"Lo sentimos, tu emprendimiento '{e.nombre}' ha sido rechazado.",
                    tipo="rechazado"
                )

        except Emprendimiento.DoesNotExist:
            pass

        return redirect("solicitudes")

    pendientes = Emprendimiento.objects.filter(
        estado="revision"
    ).order_by("-id")

    return render(
        request,
        "administracion/solicitudes.html",
        {"pendientes": pendientes}
    )


# =========================
# DESCARGAR PDF
# =========================
@login_required
@user_passes_test(es_admin)
def descargar_emprendimiento_pdf(request, emp_id):
    try:
        emp = Emprendimiento.objects.get(id=emp_id)
    except Emprendimiento.DoesNotExist:
        messages.error(request, "Emprendimiento no encontrado.")
        return redirect("solicitudes")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="emprendimiento_{emp.id}.pdf"'
    )

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    contenido = []

    contenido.append(
        Paragraph("Solicitud de Emprendimiento", styles["Title"])
    )
    contenido.append(Spacer(1, 20))

    contenido.append(
        Paragraph(f"Nombre del emprendimiento: {emp.nombre}", styles["Normal"])
    )
    contenido.append(
        Paragraph(f"Descripción: {emp.descripcion}", styles["Normal"])
    )
    contenido.append(
        Paragraph(f"Ciudad: {emp.ciudad}", styles["Normal"])
    )

    doc.build(contenido)

    return response