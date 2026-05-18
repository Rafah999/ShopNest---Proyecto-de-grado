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
    path(
        "panel-atencion/",
        views.panel_atencion,
        name="panel_atencion"
    ),
    path(
        "panel-atencion/responder/<int:ticket_id>/",
        views.responder_ticket,
        name="responder_ticket"
    ),
    path(
        "panel-atencion/cerrar/<int:ticket_id>/",
        views.cerrar_ticket,
        name="cerrar_ticket"
    ),
    path(
        "respuestas-rapidas/crear/",
        views.crear_respuesta_rapida,
        name="crear_respuesta_rapida"
    ),

    path(
        "respuestas-rapidas/editar/<int:respuesta_id>/",
        views.editar_respuesta_rapida,
        name="editar_respuesta_rapida"
    ),

    path(
        "respuestas-rapidas/eliminar/<int:respuesta_id>/",
        views.eliminar_respuesta_rapida,
        name="eliminar_respuesta_rapida"
    ),
]