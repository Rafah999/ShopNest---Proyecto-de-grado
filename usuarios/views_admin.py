from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Emprendimiento




User = get_user_model()  # apunta correctamente al CustomUser


# --- Comprobador de admin ---
def es_admin(user):
    # incluye tu flag personalizado si lo usas
    return user.is_superuser or user.is_staff or getattr(user, "is_admin_manual", False)


# --- Dashboard (admin) ---
@login_required
@user_passes_test(es_admin)
def dashboard(request):
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()

    return render(request, 'usuarios/admin/dashboard.html', {
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos
    })


# --- Listado y acciones sobre usuarios (admin) ---
@login_required
@user_passes_test(es_admin)
def usuarios_list(request):
    usuarios = User.objects.all().order_by('id')

    # Manejar acciones enviadas por POST (eliminar, promover, degradar)
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")

        if not user_id or not action:
            messages.error(request, "Solicitud inválida.")
            return redirect("lista_usuarios")

        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect("lista_usuarios")

        # Evitar que un admin se elimine o cambie a sí mismo
        if target.id == request.user.id and action in ("delete", "remove_admin"):
            messages.error(request, "No puedes realizar esa acción sobre tu propia cuenta.")
            return redirect("lista_usuarios")

        if action == "delete":
            target.delete()
            messages.success(request, f"Usuario {target.username} eliminado.")
        elif action == "make_admin":
            target.is_staff = True
            target.is_superuser = True
            target.save()
            messages.success(request, f"Usuario {target.username} promovido a administrador.")
        elif action == "remove_admin":
            target.is_staff = False
            target.is_superuser = False
            target.save()
            messages.success(request, f"Permisos de administrador removidos para {target.username}.")
        else:
            messages.error(request, "Acción desconocida.")

        return redirect("lista_usuarios")

    # GET: mostrar la lista
    return render(request, 'usuarios/admin/usuarios_list.html', {'usuarios': usuarios})

@login_required
@user_passes_test(es_admin)
def descargar_emprendimiento_pdf(request, emp_id):
    try:
        emp = Emprendimiento.objects.get(id=emp_id)
    except Emprendimiento.DoesNotExist:
        messages.error(request, "Emprendimiento no encontrado.")
        return redirect("solicitudes")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="emprendimiento_{emp.id}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    content = []

    # ===== TÍTULO =====
    content.append(Paragraph("Solicitud de Emprendimiento", styles['Title']))
    content.append(Spacer(1, 15))

    # ===== DATOS PERSONALES =====
    content.append(Paragraph("<b>Datos del Emprendedor</b>", styles['Heading2']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Nombre: {emp.nombre_emprendedor} {emp.apellidos}", styles['Normal']))
    content.append(Paragraph(f"Documento: {emp.tipo_documento} - {emp.numero_documento}", styles['Normal']))
    content.append(Paragraph(f"Fecha nacimiento: {emp.fecha_nacimiento}", styles['Normal']))

    content.append(Spacer(1, 15))

    # ===== EMPRENDIMIENTO =====
    content.append(Paragraph("<b>Información del Emprendimiento</b>", styles['Heading2']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Nombre: {emp.nombre}", styles['Normal']))
    content.append(Paragraph(f"Tipo: {emp.tipo_emprendimiento}", styles['Normal']))
    content.append(Paragraph(f"Descripción: {emp.descripcion}", styles['Normal']))
    content.append(Paragraph(f"Ubicación: {emp.ubicacion}", styles['Normal']))
    content.append(Paragraph(f"Ciudad: {emp.ciudad}", styles['Normal']))

    content.append(Spacer(1, 15))

    # ===== DETALLES =====
    content.append(Paragraph("<b>Detalles adicionales</b>", styles['Heading2']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Estático: {'Sí' if emp.es_estatico else 'No'}", styles['Normal']))
    content.append(Paragraph(f"Domicilio: {'Sí' if emp.tiene_domicilio else 'No'}", styles['Normal']))
    content.append(Paragraph(f"Método de pago: {emp.metodo_pago}", styles['Normal']))

    content.append(Spacer(1, 15))

    # ===== EDUCACIÓN =====
    content.append(Paragraph("<b>Educación</b>", styles['Heading2']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Estudiante: {'Sí' if emp.es_estudiante else 'No'}", styles['Normal']))
    content.append(Paragraph(f"Institución: {emp.institucion or 'N/A'}", styles['Normal']))
    content.append(Paragraph(f"Vende en institución: {'Sí' if emp.vende_en_institucion else 'No'}", styles['Normal']))

    doc.build(content)

    return response