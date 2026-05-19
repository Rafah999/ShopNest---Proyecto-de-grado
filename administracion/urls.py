# administracion/urls.py

from django.urls import path
from . import views

urlpatterns = [

    # DASHBOARD
    path(
        '',
        views.dashboard,
        name='admin_dashboard'
    ),

    # USUARIOS
    path(
        'usuarios/',
        views.lista_usuarios,
        name='lista_usuarios'
    ),

    # SOLICITUDES
    path(
        'solicitudes/',
        views.solicitudes,
        name='solicitudes'
    ),

    # PRODUCTOS
    path(
        'productos/',
        views.lista_productos,
        name='lista_productos'
    ),

    # COMENTARIOS
    path(
        'comentarios/',
        views.lista_comentarios,
        name='lista_comentarios'
    ),

    # CHATS
    path(
        'chats/',
        views.lista_chats,
        name='lista_chats'
    ),

    # PDF
    path(
        'emprendimiento/pdf/<int:emp_id>/',
        views.descargar_emprendimiento_pdf,
        name='descargar_pdf'
    ),
]