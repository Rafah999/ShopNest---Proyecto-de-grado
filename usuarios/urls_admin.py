from django.urls import path
from . import views_admin

urlpatterns = [
    path('administracion/', views_admin.dashboard, name='dashboard'),
    path('administracion/usuarios/', views_admin.usuarios_list, name='usuarios_list'),
]
