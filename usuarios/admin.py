from django.contrib import admin
from .models import CustomUser, Emprendimiento


@admin.register(CustomUser)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'telefono', 'is_admin_manual', 'is_staff', 'is_active')
    list_filter = ('is_admin_manual', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


@admin.register(Emprendimiento)
class EmprendimientoAdmin(admin.ModelAdmin):
    list_display = ('id','nombre','usuario','ciudad','estado')
    list_filter = ('estado','ciudad','categoria')
    search_fields = ('nombre','usuario__username','nombre_emprendedor')
