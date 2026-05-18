from django.db import models

from usuarios.models import *
from django.conf import settings

# Create your models here.
class Seguimiento(models.Model):

    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="siguiendo"
    )

    emprendimiento = models.ForeignKey(
        Emprendimiento,
        on_delete=models.CASCADE,
        related_name="seguidores"
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = (
            "usuario",
            "emprendimiento"
        )

    def __str__(self):

        return f"{self.usuario} sigue a {self.emprendimiento}"

class Favorito(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )

    creado = models.DateTimeField(auto_now_add=True)


class ComentarioProducto(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="comentarios"
    )

    comentario = models.TextField()

    creado = models.DateTimeField(auto_now_add=True)






class SolicitudContacto(models.Model):

    TIPOS = [
        ("pedido", "Hacer pedido"),
        ("disponibilidad", "Consultar disponibilidad"),
        ("personalizacion", "Consultar personalización"),
        ("pago", "Métodos de pago"),
        ("chat", "Hablar con el vendedor"),
    ]

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("respondida", "Respondida"),
        ("cerrada", "Cerrada"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solicitudes_contacto"
    )

    emprendimiento = models.ForeignKey(
        Emprendimiento,
        on_delete=models.CASCADE,
        related_name="solicitudes_contacto"
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPOS
    )

    mensaje = models.TextField(
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="pendiente"
    )

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_display()}"
    

# =========================
# CHAT
# =========================
class Chat(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chats"
    )

    emprendimiento = models.ForeignKey(
        Emprendimiento,
        on_delete=models.CASCADE,
        related_name="chats"
    )

    # Último producto consultado en el chat
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "usuario",
            "emprendimiento"
        )
        ordering = ["-actualizado"]

    def __str__(self):
        return f"{self.usuario.username} - {self.emprendimiento.nombre}"

# =========================
# MENSAJES DEL CHAT
# =========================
class MensajeChat(models.Model):

    TIPOS = [
        ("sistema", "Sistema"),
        ("usuario", "Usuario"),
        ("emprendedor", "Emprendedor"),
    ]

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="mensajes"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default="sistema"
    )

    contenido = models.TextField()

    fecha = models.DateTimeField(auto_now_add=True)

    def get_producto_id(self):
        if self.contenido.startswith("__PRODUCTO__:"):
            try:
                return int(self.contenido.split(":")[1])
            except (IndexError, ValueError):
                return None
        return None

    class Meta:
        ordering = ["fecha"]

    def __str__(self):
        return f"{self.chat.id} - {self.tipo}"