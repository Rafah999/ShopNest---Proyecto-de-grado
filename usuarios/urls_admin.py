from django.urls import path
from . import views_admin

urlpatterns = [
    path('administracion/', views_admin.dashboard, name='dashboard'),
    path('administracion/usuarios/', views_admin.usuarios_list, name='usuarios_list'),
    path('administracion/emprendimiento/pdf/<int:emp_id>/',views_admin.descargar_emprendimiento_pdf,name='descargar_pdf'),
]
