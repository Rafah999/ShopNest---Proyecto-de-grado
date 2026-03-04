from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model

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

