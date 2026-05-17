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
  
    path("crear-emprendimiento/", views.crear_emprendimiento, name="crear_emprendimiento"),
    path("solicitud-enviada/", views.solicitud_enviada, name="solicitud_enviada"),
    path('mi-emprendimiento/', views.mi_emprendimiento, name='mi_emprendimiento'),
    path("api/notificaciones/", views.obtener_notificaciones, name="obtener_notificaciones"),
    path("api/notificaciones/marcar/", views.marcar_notificaciones_vistas, name="marcar_notificaciones"),
    path("gestor-emprendimiento/", views.gestor_emprendimiento, name="gestor_emprendimiento"),
    path("actualizar-stock/", views.actualizar_stock, name="actualizar_stock"),
    path("toggle-visibility/", views.toggle_visibility,name="toggle_visibility"),
    path("emprendimiento/<int:id>/", views.ver_emprendimiento, name="ver_emprendimiento"),
    path("producto/<int:id>/", views.ver_producto, name="ver_producto"),
    path("categorias/", views.categorias, name="categorias"),
    path('producto/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('imagen-carrusel/editar/<int:imagen_id>/', views.actualizar_imagen_carrusel, name='editar_img_carrusel'),
    path("imagen-carrusel/eliminar/<int:imagen_id>/", views.eliminar_imagen_carrusel, name="eliminar_imagen_carrusel"),
] 
