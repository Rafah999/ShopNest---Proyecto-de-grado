from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.dashboard,
        name='admin_dashboard'
    ),

    path(
        'usuarios/',
        views.usuarios_list,
        name='lista_usuarios'
    ),

    path(
        'solicitudes/',
        views.solicitudes,
        name='solicitudes'
    ),

    path(
        'emprendimiento/pdf/<int:emp_id>/',
        views.descargar_emprendimiento_pdf,
        name='descargar_pdf'
    ),
]