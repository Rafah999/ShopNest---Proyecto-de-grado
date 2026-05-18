from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from usuarios.models import *
from .models import *
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


from usuarios.models import Notificacion


def crear_notificacion_panel(usuario):
    """
    Crea una sola notificación de Panel de Atención
    mientras exista una no leída.
    """

    existe = Notificacion.objects.filter(
        usuario=usuario,
        tipo="panel_atencion",
        estado="no_leido"
    ).exists()

    if not existe:
        Notificacion.objects.create(
            usuario=usuario,
            tipo="panel_atencion",
            mensaje="Tienes novedades en tu Panel de Atención."
        )


@login_required
@require_POST
def toggle_seguimiento(request, emprendimiento_id):

    emprendimiento = get_object_or_404(
        Emprendimiento,
        id=emprendimiento_id
    )

    seguimiento = Seguimiento.objects.filter(
        usuario=request.user,
        emprendimiento=emprendimiento
    ).first()

    if seguimiento:
        seguimiento.delete()
        siguiendo = False
    else:
        Seguimiento.objects.create(
            usuario=request.user,
            emprendimiento=emprendimiento
        )
        siguiendo = True

    total_seguidores = Seguimiento.objects.filter(
        emprendimiento=emprendimiento
    ).count()

    # Si es AJAX
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "siguiendo": siguiendo,
            "total_seguidores": total_seguidores
        })

    # Si viene de un form normal
    return redirect("ver_emprendimiento", id=emprendimiento.id)


@login_required
@require_POST
def crear_solicitud_contacto(request, producto_id):

    producto = get_object_or_404(
        Producto,
        id=producto_id
    )

    tipo = request.POST.get("tipo")
    mensaje = request.POST.get("mensaje", "").strip()

    SolicitudContacto.objects.create(
        usuario=request.user,
        emprendimiento=producto.emprendimiento,
        producto=producto,
        tipo=tipo,
        mensaje=mensaje
    )

    messages.success(
        request,
        "Tu solicitud fue enviada al vendedor."
    )

    return redirect("ver_producto", id=producto.id)



@login_required
def contacto_producto(request, producto_id):

    producto = get_object_or_404(
        Producto,
        id=producto_id
    )

    # Un solo chat por usuario y emprendimiento
    chat, creado = Chat.objects.get_or_create(
        usuario=request.user,
        emprendimiento=producto.emprendimiento,
        defaults={
            "producto": producto
        }
    )

    # Detectar si el usuario está contactando un producto diferente
    producto_cambio = chat.producto_id != producto.id

    # Actualizar el producto actual del chat
    chat.producto = producto
    chat.save(update_fields=["producto", "actualizado"])

    # Si es un chat nuevo, crear mensaje inicial
    if creado:
        MensajeChat.objects.create(
            chat=chat,
            tipo="sistema",
            contenido=(
                f"Has iniciado una conversación con "
                f"'{producto.emprendimiento.nombre}'."
            )
        )

    # Si es un producto diferente, guardar un marcador para que
    # el template renderice la tarjeta del producto dentro del chat
    if creado or producto_cambio:
        MensajeChat.objects.create(
            chat=chat,
            tipo="sistema",
            contenido=f"__PRODUCTO__:{producto.id}"
        )

    tipo_preseleccionado = request.GET.get("tipo", "")

    return redirect(
        f"{reverse('mis_chats')}?chat={chat.id}&tipo={tipo_preseleccionado}"
    )

@login_required
def mis_chats(request):
    chats = (
        Chat.objects
        .filter(usuario=request.user)
        .select_related(
            "emprendimiento",
            "producto"
        )
        .prefetch_related("mensajes")
        .order_by("-actualizado")
    )

    chat_activo = None
    chat_id = request.GET.get("chat")

    if chat_id:
        chat_activo = chats.filter(id=chat_id).first()

    if not chat_activo and chats.exists():
        chat_activo = chats.first()

    # ----------------------------------------
    # LÓGICA DE VISIBILIDAD
    # ----------------------------------------

    # Mostrar tarjeta + formulario solo cuando:
    # 1. Hay un producto asociado
    # 2. Aún no se ha enviado ninguna solicitud en este flujo
    mostrar_contacto_producto = False

    if chat_activo and chat_activo.producto:
        # Si no hay mensajes o si el último mensaje NO es del sistema,
        # se considera que todavía no se completó el flujo.
        ultimo = chat_activo.mensajes.last()

        if not ultimo:
            mostrar_contacto_producto = True
        else:
            # Si ya existe una solicitud enviada, el sistema habrá
            # agregado mensajes al chat, así que ya no se muestra.
            mostrar_contacto_producto = False

    # Mostrar opciones adicionales solo cuando:
    # 1. Existe producto asociado
    # 2. Ya existen mensajes
    mostrar_opciones_adicionales = False

    if (
        chat_activo
        and chat_activo.producto
        and chat_activo.mensajes.exists()
        and not mostrar_contacto_producto
    ):
        mostrar_opciones_adicionales = True

    return render(
        request,
        "social/chats.html",
        {
            "chats": chats,
            "chat_activo": chat_activo,
            "mostrar_contacto_producto": mostrar_contacto_producto,
            "mostrar_opciones_adicionales": mostrar_opciones_adicionales,
        }
    )

@login_required
def mis_chats(request):
    chats = (
        Chat.objects
        .filter(usuario=request.user)
        .select_related(
            "emprendimiento",
            "producto"
        )
        .prefetch_related("mensajes")
        .order_by("-actualizado")
    )

    chat_activo = None
    chat_id = request.GET.get("chat")

    if chat_id:
        chat_activo = chats.filter(id=chat_id).first()

    if not chat_activo and chats.exists():
        chat_activo = chats.first()

    # SOLO se considera que viene desde un producto
    # si el parámetro tipo existe Y tiene contenido.
    tipo_preseleccionado = request.GET.get("tipo", "").strip()
    viene_desde_producto = bool(tipo_preseleccionado)

    # Mostrar tarjeta del producto + formulario
    mostrar_contacto_producto = (
        chat_activo is not None
        and chat_activo.producto is not None
        and viene_desde_producto
    )

    # Mostrar opciones adicionales únicamente
    # si ya no estamos mostrando el formulario
    mostrar_opciones_adicionales = (
        chat_activo is not None
        and not mostrar_contacto_producto
        and chat_activo.mensajes.exists()
    )

    return render(
        request,
        "social/chats.html",
        {
            "chats": chats,
            "chat_activo": chat_activo,
            "mostrar_contacto_producto": mostrar_contacto_producto,
            "mostrar_opciones_adicionales": mostrar_opciones_adicionales,
            "tipo_preseleccionado": tipo_preseleccionado,
        }
    )



@login_required
@require_POST
def enviar_mensaje_chat(request):

    from django.utils import timezone
    from datetime import timedelta

    chat_id = request.POST.get("chat_id")
    tipo = request.POST.get("tipo")
    mensaje = request.POST.get("mensaje", "").strip()

    chat = get_object_or_404(
        Chat,
        id=chat_id,
        usuario=request.user
    )

    if not tipo:
        return JsonResponse({
            "success": False,
            "error": "Debes seleccionar una opción."
        })

    # Validar que el chat tenga un producto asociado
    if not chat.producto:
        return JsonResponse({
            "success": False,
            "error": (
                "Debes seleccionar un producto antes de enviar "
                "una solicitud."
            )
        })

    # --------------------------------------------------
    # LÍMITE GLOBAL DIARIO (ANTI-SPAM)
    # --------------------------------------------------
    hoy = timezone.now().date()

    total_hoy = SolicitudContacto.objects.filter(
        usuario=request.user,
        fecha__date=hoy
    ).count()

    if total_hoy >= 10:
        return JsonResponse({
            "success": False,
            "error": (
                "Has alcanzado el límite diario de solicitudes."
            )
        })

    # --------------------------------------------------
    # BLOQUEO DE 4 HORAS PARA EL MISMO PRODUCTO
    # --------------------------------------------------
    limite_respuesta = timezone.now() - timedelta(hours=4)

    solicitud_reciente = SolicitudContacto.objects.filter(
        usuario=request.user,
        emprendimiento=chat.emprendimiento,
        producto=chat.producto,
        estado="pendiente",
        fecha__gte=limite_respuesta
    ).exists()

    if solicitud_reciente:
        return JsonResponse({
            "success": False,
            "error": (
                "Ya enviaste una solicitud para este producto. "
                "Debes esperar hasta 4 horas para enviar otra "
                "si el vendedor aún no responde."
            )
        })

    # --------------------------------------------------
    # CREAR TICKET
    # --------------------------------------------------
    ticket = SolicitudContacto.objects.create(
        usuario=request.user,
        emprendimiento=chat.emprendimiento,
        producto=chat.producto,
        tipo=tipo,
        mensaje=mensaje,
        estado="pendiente"
    )

    crear_notificacion_panel(chat.emprendimiento.usuario)

    # --------------------------------------------------
    # MENSAJE PRINCIPAL DEL USUARIO
    # --------------------------------------------------
    mensaje_usuario = (
        f"Solicitud sobre el producto "
        f"'{chat.producto.nombre}': "
        f"{ticket.get_tipo_display()}"
    )

    MensajeChat.objects.create(
        chat=chat,
        tipo="usuario",
        contenido=mensaje_usuario
    )

    # Mensaje adicional del usuario
    if mensaje:
        MensajeChat.objects.create(
            chat=chat,
            tipo="usuario",
            contenido=mensaje
        )

    # --------------------------------------------------
    # RESPUESTA AUTOMÁTICA DEL SISTEMA
    # --------------------------------------------------
    respuesta_sistema = (
        f"Se ha generado un ticket de atención "
        f"relacionado con el producto "
        f"'{chat.producto.nombre}'. "
        f"El vendedor responderá lo antes posible."
    )

    MensajeChat.objects.create(
        chat=chat,
        tipo="sistema",
        contenido=respuesta_sistema
    )

    # --------------------------------------------------
    # NOTIFICACIÓN AL EMPRENDEDOR
    # --------------------------------------------------
    Notificacion.objects.create(
        usuario=chat.emprendimiento.usuario,
        mensaje=(
            f"{request.user.username} ha enviado una solicitud "
            f"de tipo '{ticket.get_tipo_display()}' "
            f"para el producto '{chat.producto.nombre}'."
        ),
        tipo="info"
    )

    # --------------------------------------------------
    # RESPUESTA AJAX
    # --------------------------------------------------
    return JsonResponse({
        "success": True,
        "mensaje_usuario": mensaje_usuario,
        "mensaje_adicional": mensaje,
        "respuesta_sistema": respuesta_sistema,
    })


@login_required
def panel_atencion(request):

    emprendimiento = get_object_or_404(
        Emprendimiento,
        usuario=request.user
    )

    historial = request.GET.get("historial") == "1"

    # Base queryset
    tickets = (
        SolicitudContacto.objects
        .filter(emprendimiento=emprendimiento)
        .select_related("usuario", "producto")
    )

    # Panel principal vs historial
    if historial:
        tickets = tickets.filter(estado="cerrada")
    else:
        tickets = tickets.exclude(estado="cerrada")

    # Filtros
    estado = request.GET.get("estado", "")
    tipo = request.GET.get("tipo", "")

    if estado:
        tickets = tickets.filter(estado=estado)

    if tipo:
        tickets = tickets.filter(tipo=tipo)

    tickets = tickets.order_by("fecha")

    # Ticket activo
    ticket_activo = None
    ticket_id = request.GET.get("ticket")

    if ticket_id:
        ticket_activo = tickets.filter(id=ticket_id).first()

    if not ticket_activo and tickets.exists():
        ticket_activo = tickets.first()


    base = SolicitudContacto.objects.filter(
        emprendimiento=emprendimiento
    )

    # Hoy
    hoy = timezone.now().date()

    tickets_hoy = base.filter(
        fecha__date=hoy
    ).count()

    # Últimos 7 días
    ultima_semana = timezone.now() - timedelta(days=7)

    tickets_semana = base.filter(
        fecha__gte=ultima_semana
    ).count()

    # Tasa de cierre
    total_tickets = base.count()

    if total_tickets > 0:
        tasa_cierre = round(
            (base.filter(estado="cerrada").count() / total_tickets) * 100,
            1
        )
    else:
        tasa_cierre = 0

    # Tipo más frecuente
    tipo_top = (
        base.values("tipo")
        .annotate(total=models.Count("id"))
        .order_by("-total")
        .first()
    )

    if tipo_top:
        tipo_mas_frecuente = dict(
            SolicitudContacto.TIPOS
        ).get(tipo_top["tipo"], "N/A")
    else:
        tipo_mas_frecuente = "N/A"

    context = {
        "tickets": tickets,
        "ticket_activo": ticket_activo,
        "historial": historial,

        "estado_actual": estado,
        "tipo_actual": tipo,
        "tipos": SolicitudContacto.TIPOS,

        "total_filtrados": tickets.count(),

        "total_pendientes": base.filter(
            estado="pendiente"
        ).count(),

        "total_respondidos": base.filter(
            estado="respondida"
        ).count(),

        "total_cerrados": base.filter(
            estado="cerrada"
        ).count(),

        "total_pedidos": base.filter(
            tipo="pedido"
        ).count(),

        "total_consultas": base.exclude(
            tipo="pedido"
        ).count(),
        "tickets_hoy": tickets_hoy,
        "tickets_semana": tickets_semana,
        "tasa_cierre": tasa_cierre,
        "tipo_mas_frecuente": tipo_mas_frecuente,
        "respuestas_rapidas": emprendimiento.respuestas_rapidas.all(),
    }

    return render(
        request,
        "social/panel_atencion.html",
        context
    )





@login_required
@require_POST
def responder_ticket(request, ticket_id):

    emprendimiento = get_object_or_404(
        Emprendimiento,
        usuario=request.user
    )

    ticket = get_object_or_404(
        SolicitudContacto,
        id=ticket_id,
        emprendimiento=emprendimiento
    )

    respuesta = request.POST.get("respuesta", "").strip()

    if not respuesta:
        messages.error(
            request,
            "Debes escribir una respuesta."
        )
        return redirect(
            f"{reverse('panel_atencion')}?ticket={ticket.id}"
        )

    chat = Chat.objects.filter(
        usuario=ticket.usuario,
        emprendimiento=ticket.emprendimiento
    ).first()

    if chat:
        MensajeChat.objects.create(
            chat=chat,
            tipo="emprendedor",
            contenido=respuesta
        )

    ticket.estado = "respondida"
    ticket.save(update_fields=["estado"])

    Notificacion.objects.create(
        usuario=ticket.usuario,
        mensaje=(
            f"{ticket.emprendimiento.nombre} ha respondido "
            f"tu solicitud."
        ),
        tipo="info"
    )

    messages.success(
        request,
        "Respuesta enviada correctamente."
    )

    return redirect(
        f"{reverse('panel_atencion')}?ticket={ticket.id}"
    )



@login_required
def cerrar_ticket(request, ticket_id):

    emprendimiento = get_object_or_404(
        Emprendimiento,
        usuario=request.user
    )

    ticket = get_object_or_404(
        SolicitudContacto,
        id=ticket_id,
        emprendimiento=emprendimiento
    )

    # Cerrar ticket
    ticket.estado = "cerrada"
    ticket.save(update_fields=["estado"])

    # Buscar siguiente ticket pendiente
    siguiente = (
        SolicitudContacto.objects
        .filter(
            emprendimiento=emprendimiento,
            estado="pendiente"
        )
        .order_by("fecha")
        .first()
    )

    if siguiente:
        return redirect(
            f"{reverse('panel_atencion')}?ticket={siguiente.id}"
        )

    return redirect("panel_atencion")



@login_required
@require_POST
def crear_respuesta_rapida(request):

    emprendimiento = get_object_or_404(
        Emprendimiento,
        usuario=request.user
    )

    titulo = request.POST.get("titulo", "").strip()
    contenido = request.POST.get("contenido", "").strip()

    if titulo and contenido:
        RespuestaRapida.objects.create(
            emprendimiento=emprendimiento,
            titulo=titulo,
            contenido=contenido
        )

    return redirect("panel_atencion")


@login_required
@require_POST
def editar_respuesta_rapida(request, respuesta_id):

    emprendimiento = get_object_or_404(
        Emprendimiento,
        usuario=request.user
    )

    respuesta = get_object_or_404(
        RespuestaRapida,
        id=respuesta_id,
        emprendimiento=emprendimiento
    )

    titulo = request.POST.get("titulo", "").strip()
    contenido = request.POST.get("contenido", "").strip()

    if titulo and contenido:
        respuesta.titulo = titulo
        respuesta.contenido = contenido
        respuesta.save()

    return redirect("panel_atencion")


@login_required
def eliminar_respuesta_rapida(request, respuesta_id):

    emprendimiento = get_object_or_404(
        Emprendimiento,
        usuario=request.user
    )

    respuesta = get_object_or_404(
        RespuestaRapida,
        id=respuesta_id,
        emprendimiento=emprendimiento
    )

    respuesta.delete()

    return redirect("panel_atencion")

