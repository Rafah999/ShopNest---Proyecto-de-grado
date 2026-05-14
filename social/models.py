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