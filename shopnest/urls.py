from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path("social/", include("social.urls")),
    path('administracion/', include('administracion.urls')),
]

# SERVIR ARCHIVOS MEDIA EN DESARROLLO
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)