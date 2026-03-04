from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# =========================
# Usuario personalizado
# =========================
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    is_admin_manual = models.BooleanField(default=False)

    foto_perfil = models.ImageField(
        upload_to="perfiles/",
        blank=True,
        null=True,
        default="perfiles/default_user.png"
    )

    def __str__(self):
        return self.username


# =========================
# Emprendimiento
# =========================
class Emprendimiento(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emprendimientos"
    )

    # Datos personales
    nombre_emprendedor = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    tipo_documento = models.CharField(max_length=20)
    numero_documento = models.CharField(max_length=50)

    # Datos del emprendimiento
    nombre = models.CharField(max_length=100)
    tipo_emprendimiento = models.CharField(max_length=50)
    fecha_creacion = models.DateField(null=True, blank=True)
    descripcion = models.TextField()

    es_estatico = models.BooleanField(default=False)
    tiene_domicilio = models.BooleanField(default=False)
    metodo_pago = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)

    # Educación
    es_estudiante = models.BooleanField(default=False)
    institucion = models.CharField(max_length=150, blank=True, null=True)
    vende_en_institucion = models.BooleanField(default=False)

    # Archivos
    logo = models.FileField(upload_to="logos/", null=True, blank=True)
    igms_productos = models.FileField(upload_to="igms/", null=True, blank=True)
    documento_identidad = models.FileField(upload_to="documentos/", null=True, blank=True)

    ciudad = models.CharField(max_length=50)

    ESTADOS = [
        ("revision", "En revisión"),
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="revision"
    )

    # 👇 CORREGIDO: evita error de migraciones
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"
