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