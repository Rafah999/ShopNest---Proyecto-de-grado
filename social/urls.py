from django.urls import path
from . import views

urlpatterns = [
    path(
        "seguir/<int:emprendimiento_id>/",
        views.toggle_seguimiento,
        name="toggle_seguimiento"
    ),

    path(
        "contactar/<int:producto_id>/",
        views.contacto_producto,
        name="contacto_producto"
    ),

    path(
        "chats/",
        views.mis_chats,
        name="mis_chats"
    ),
    path(
        "chats/enviar/",
        views.enviar_mensaje_chat,
        name="enviar_mensaje_chat"
    ),
]