from django.urls import path
from . import views

urlpatterns = [
    # --- Rutas públicas ---
    path("", views.index, name="index"),
    path("register/", views.registro, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("perfil/", views.perfil, name="perfil"),

    # --- Rutas generales del dashboard (si aplica a todos) ---
    path("dashboard/", views.dashboard, name="dashboard"),

    # --- Rutas exclusivas para el área de administración ---
    path("administracion/", views.dashboard, name="admin_dashboard"),
    path("administracion/usuarios/", views.lista_usuarios, name="lista_usuarios"),
    path("administracion/solicitudes/", views.solicitudes, name="solicitudes"),
    path("crear-emprendimiento/", views.crear_emprendimiento, name="crear_emprendimiento"),
    path("solicitud-enviada/", views.solicitud_enviada, name="solicitud_enviada"),

]
