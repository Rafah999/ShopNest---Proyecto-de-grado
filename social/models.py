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

