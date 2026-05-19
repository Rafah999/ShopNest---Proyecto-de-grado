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
    es_emprendedor = models.BooleanField(default=False)
    vio_tutorial_emprendimiento = models.BooleanField(default=False)
    foto_perfil = models.ImageField(
        upload_to="perfiles/",
        blank=True,
        null=True,
        default="perfiles/default_user.png"
    )

    def __str__(self):
        return self.username

class CategoriaProducto(models.Model):

    codigo = models.CharField(
        max_length=10,
        unique=True,
        blank=True
    )

    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    creada = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # SI NO TIENE CODIGO
        if not self.codigo:

            ultima = CategoriaProducto.objects.order_by("-id").first()

            if ultima:

                numero = int(ultima.codigo) + 1

            else:

                numero = 1

            self.codigo = str(numero).zfill(2)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


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
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emprendimientos"
    )
    fecha_creacion = models.DateField(null=True, blank=True)
    descripcion = models.TextField()

    es_estatico = models.BooleanField(default=False)
    tiene_domicilio = models.BooleanField(default=False)
    metodo_pago = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)

    publicado = models.BooleanField(default=False)
    personalizado = models.BooleanField(default=False)


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
    mostrar_ubicacion = models.BooleanField(default=False)

    google_maps = models.TextField(
        blank=True,
        null=True
    )

    # 👇 CORREGIDO: evita error de migraciones
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"


class Notificacion(models.Model):

    TIPOS = [
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
        ("info", "Información"),
    ]

    ESTADOS = [
        ("no_leido", "No leído"),
        ("visto", "Visto"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones"
    )

    mensaje = models.TextField()

    tipo = models.CharField(max_length=20, choices=TIPOS)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="no_leido")

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo}"


class EmprendimientoImagen(models.Model):
    emprendimiento = models.ForeignKey(
        Emprendimiento,
        on_delete=models.CASCADE,
        related_name="imagenes"
    )

    imagen = models.ImageField(upload_to="emprendimientos/galeria/")

    orden = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Imagen {self.id} - {self.emprendimiento.nombre}"
    

class Producto(models.Model):

   

    emprendimiento = models.ForeignKey(
        Emprendimiento,
        on_delete=models.CASCADE,
        related_name="productos"
    )

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos"
    )
    imagen = models.ImageField(upload_to="productos/")
    stock = models.PositiveIntegerField(default=0)
    stock_indefinido = models.BooleanField(
        default=False
    )

    visible = models.BooleanField(default=True)

    disponible = models.BooleanField(default=True)

    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre



class ValoracionProducto(models.Model):

    ESTRELLAS = [
        (1, "1 estrella"),
        (2, "2 estrellas"),
        (3, "3 estrellas"),
        (4, "4 estrellas"),
        (5, "5 estrellas"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="valoraciones_productos"
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="valoraciones"
    )

    calificacion = models.PositiveSmallIntegerField(
        choices=ESTRELLAS
    )

    comentario = models.TextField(
        blank=True,
        null=True
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "usuario",
            "producto"
        )
        ordering = ["-fecha"]

    def __str__(self):
        return (
            f"{self.usuario.username} - "
            f"{self.producto.nombre} "
            f"({self.calificacion}★)"
        )