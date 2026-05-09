from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model, authenticate, login
from usuarios.models import CustomUser
from django.contrib import messages
from .forms import ProductoForm, RegistroForm, LoginForm, EmprendimientoForm, FotoPerfilForm
from .models import Emprendimiento, Notificacion
from django.http import JsonResponse
from .models import *
from django.views.decorators.http import require_POST


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
            print(form.errors)  # 🔥 ESTO ES CLAVE
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
            messages.error(request, "Usuario o contraseña incorrectos.")

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

    # 🔥 OBTENER EMPRENDIMIENTO DEL USUARIO
    emprendimiento = Emprendimiento.objects.filter(usuario=request.user).order_by("-id").first()

    return render(request, "usuarios/perfil.html", {
        "usuario": request.user,
        "form": form,
        "emprendimiento": emprendimiento
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

    pendientes = Emprendimiento.objects.filter(estado="revision").order_by("-id")
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


@login_required
def mi_emprendimiento(request):

    emprendimiento = Emprendimiento.objects.filter(
        usuario=request.user,
        estado="aprobado"
    ).first()

    if not emprendimiento:
        return redirect("perfil")

    if emprendimiento.publicado:
        return redirect("gestor_emprendimiento")

    # =========================
    # LOGO
    # =========================
    if request.method == "POST":

        tipo = request.POST.get("tipo")

        # LOGO
        if tipo == "logo":

            logo = request.FILES.get("logo")

            if logo:
                emprendimiento.logo = logo
                emprendimiento.save()

        # IMAGENES
        elif tipo == "imagenes":

            archivos = request.FILES.getlist("imagenes")

            if emprendimiento.imagenes.count() < 5:

                for archivo in archivos:

                    if emprendimiento.imagenes.count() < 5:

                        EmprendimientoImagen.objects.create(
                            emprendimiento=emprendimiento,
                            imagen=archivo
                        )

        # PRODUCTOS
        elif tipo == "producto":

            form_producto = ProductoForm(
                request.POST,
                request.FILES
            )

            if form_producto.is_valid():

                producto = form_producto.save(commit=False)

                producto.emprendimiento = emprendimiento

                producto.save()

        # PUBLICAR
        elif tipo == "publicar":

            puede_publicar = (
                emprendimiento.logo and
                emprendimiento.imagenes.count() >= 5 and
                emprendimiento.productos.count() >= 3
            )

            if puede_publicar:

                emprendimiento.publicado = True
                emprendimiento.save()

                return redirect("gestor_emprendimiento")

        return redirect("mi_emprendimiento")

    producto_form = ProductoForm()

    puede_publicar = (
        emprendimiento.logo and
        emprendimiento.imagenes.count() >= 5 and
        emprendimiento.productos.count() >= 3
    )

    mostrar_tutorial = False

    if not request.user.vio_tutorial_emprendimiento:
        mostrar_tutorial = True
        request.user.vio_tutorial_emprendimiento = True
        request.user.save()

    return render(request, "usuarios/mi_emprendimiento.html", {
        "emprendimiento": emprendimiento,
        "producto_form": producto_form,
        "puede_publicar": puede_publicar,
        "mostrar_tutorial": mostrar_tutorial,
    })


@login_required
def gestor_emprendimiento(request):

    emprendimiento = Emprendimiento.objects.filter(
        usuario=request.user,
        estado="aprobado",
        publicado=True
    ).first()

    if not emprendimiento:
        return redirect("crear_emprendimiento")

    productos = emprendimiento.productos.all()
    imagenes = emprendimiento.imagenes.all()

    producto_form = ProductoForm()

    # =========================
    # REGISTRAR PRODUCTO
    # =========================
    if request.method == "POST":

        tipo = request.POST.get("tipo")

        # =========================
        # LOGO
        # =========================
        if tipo == "logo":

            logo = request.FILES.get("logo")

            if logo:
                emprendimiento.logo = logo
                emprendimiento.save()

        # =========================
        # IMÁGENES
        # =========================
        elif tipo == "imagenes":

            archivos = request.FILES.getlist("imagenes")

            for archivo in archivos:

                EmprendimientoImagen.objects.create(
                    emprendimiento=emprendimiento,
                    imagen=archivo
                )

        # =========================
        # PRODUCTOS
        # =========================
        elif tipo == "producto":

            producto_form = ProductoForm(
                request.POST,
                request.FILES
            )

            if producto_form.is_valid():

                producto = producto_form.save(commit=False)

                producto.emprendimiento = emprendimiento

                producto.save()

        # =========================
        # PUBLICAR
        # =========================
        elif tipo == "publicar":

            total_imagenes = imagenes.count()
            total_productos = productos.count()

            if (
                emprendimiento.logo and
                total_imagenes >= 5 and
                total_productos >= 3
            ):

                emprendimiento.publicado = True
                emprendimiento.estado = "aprobado"

                emprendimiento.save()

                request.user.es_emprendedor = True
                request.user.save()

        return redirect("gestor_emprendimiento")

    puede_publicar = (
        emprendimiento.logo and
        imagenes.count() >= 5 and
        productos.count() >= 3
    )

    return render(request,
        "usuarios/gestor_emprendimiento.html",
        {
            "emprendimiento": emprendimiento,
            "productos": productos,
            "imagenes": imagenes,
            "producto_form": producto_form,
            "puede_publicar": puede_publicar
        }
    )


@login_required
def obtener_notificaciones(request):
    notificaciones = request.user.notificaciones.all().order_by("-fecha")

    data = []

    for n in notificaciones:
        data.append({
            "id": n.id,
            "mensaje": n.mensaje,
            "estado": n.estado,
            "fecha": n.fecha.strftime("%d/%m/%Y %H:%M")
        })

    return JsonResponse(data, safe=False)

@login_required
def marcar_notificaciones_vistas(request):
    request.user.notificaciones.filter(estado="no_leido").update(estado="visto")
    return JsonResponse({"ok": True})



@require_POST
@login_required
def actualizar_stock(request):

    producto_id = request.POST.get("producto_id")
    stock = request.POST.get("stock")

    try:

        producto = Producto.objects.get(
            id=producto_id,
            emprendimiento__usuario=request.user
        )

        producto.stock = int(stock)
        producto.save()

        return JsonResponse({
            "success": True,
            "stock": producto.stock
        })

    except:

        return JsonResponse({
            "success": False
        })
    


@require_POST
@login_required
def toggle_visibility(request):

    producto_id = request.POST.get("producto_id")

    try:

        producto = Producto.objects.get(
            id=producto_id,
            emprendimiento__usuario=request.user
        )

        producto.visible = not producto.visible
        producto.save()

        return JsonResponse({
            "success": True,
            "visible": producto.visible
        })

    except:

        return JsonResponse({
            "success": False
        })