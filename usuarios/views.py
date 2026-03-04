from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model

from .forms import RegistroForm, LoginForm, EmprendimientoForm, FotoPerfilForm
from .models import Emprendimiento

User = get_user_model()  # Modelo de usuario personalizado


# --- Página de inicio ---
def index(request):
    return render(request, "base.html", {
        "body_class": "inicio-page",
        "mostrar_mensaje": not request.user.is_authenticated
    })


# --- Registro ---
def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            if user.is_superuser or user.is_staff or getattr(user, 'is_admin_manual', False):
                return redirect("admin_dashboard")
            return redirect("index")
    else:
        form = RegistroForm()

    return render(request, "usuarios/registro.html", {
        "form": form,
        "body_class": "register-page"
    })


# --- Login ---
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_superuser or user.is_staff or getattr(user, 'is_admin_manual', False):
                return redirect("admin_dashboard")
            return redirect("index")
    else:
        form = LoginForm()

    return render(request, "usuarios/login.html", {
        "form": form,
        "body_class": "login-page"
    })


# --- Logout ---
def user_logout(request):
    logout(request)
    return redirect("index")


# --- Perfil de usuario ---
@login_required
def perfil(request):
    if request.method == "POST":
        form = FotoPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("perfil")
    else:
        form = FotoPerfilForm(instance=request.user)

    return render(request, "usuarios/perfil.html", {
        "usuario": request.user,
        "form": form
    })


# --- Verificar si es admin ---
def es_admin(user):
    return user.is_superuser or user.is_staff or getattr(user, 'is_admin_manual', False)


# --- Admin Dashboard ---
@login_required
@user_passes_test(es_admin)
def dashboard(request):
    return render(request, "usuarios/admin/dashboard.html")


# --- Listado de usuarios ---
@login_required
@user_passes_test(es_admin)
def lista_usuarios(request):
    usuarios = User.objects.all().order_by('id')

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

    return render(request, "usuarios/admin/usuarios_list.html", {"usuarios": usuarios})


# --- Solicitudes ---
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
                e.save()
            elif action == "rechazar":
                e.estado = "rechazado"
                e.save()
        except Emprendimiento.DoesNotExist:
            pass

        return redirect("solicitudes")

    pendientes = Emprendimiento.objects.filter(estado="pendiente").order_by("-id")
    return render(request, "usuarios/admin/solicitudes.html", {"pendientes": pendientes})


# --- Crear emprendimiento ---
@login_required
def crear_emprendimiento(request):

    if request.method == "POST":
        form = EmprendimientoForm(request.POST, request.FILES)
        if form.is_valid():
            emprendimiento = form.save(commit=False)
            emprendimiento.usuario = request.user
            emprendimiento.estado = "revision"
            emprendimiento.save()
            return redirect("solicitud_enviada")
    else:
        form = EmprendimientoForm()

    return render(request, "usuarios/crear_emprendimiento.html", {"form": form})



@login_required
def solicitud_enviada(request):
    return render(request, "usuarios/solicitud_enviada.html")
