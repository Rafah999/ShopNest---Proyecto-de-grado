from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Emprendimiento
from .models import *


# =========================
# Registro
# =========================
class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telefono = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "telefono", "password1", "password2")


class LoginForm(AuthenticationForm):
    pass


class FotoPerfilForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("foto_perfil",)


# =========================
# Emprendimiento
# =========================
class EmprendimientoForm(forms.ModelForm):

    # =========================
    # CHOICES PERSONALIZADOS
    # =========================

    TIPO_DOCUMENTO_CHOICES = [
        ("cc", "Cédula de Ciudadanía"),
        ("ti", "Tarjeta de Identidad"),
        ("ce", "Cédula de Extranjería"),
    ]

    METODO_PAGO_CHOICES = [
        ("efectivo", "Efectivo"),
        ("transferencia", "Transferencia"),
        ("tarjeta", "Tarjeta"),
    ]

    # 🔥 tipo documento como select
    tipo_documento = forms.ChoiceField(
        choices=TIPO_DOCUMENTO_CHOICES
    )

    # 🔥 método de pago MULTIPLE
    metodo_pago = forms.MultipleChoiceField(
        choices=METODO_PAGO_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    # 🔥 ciudad fija
    ciudad = forms.CharField(
        initial="Cartagena",
        disabled=True
    )

    # 🔥 booleanos estilo SI/NO
    es_estatico = forms.ChoiceField(
        choices=[("True", "Sí"), ("False", "No")],
        widget=forms.RadioSelect
    )

    

    tiene_domicilio = forms.ChoiceField(
        choices=[("True", "Sí"), ("False", "No")],
        widget=forms.RadioSelect
    )

    es_estudiante = forms.ChoiceField(
        choices=[("True", "Sí"), ("False", "No")],
        widget=forms.RadioSelect
    )

    vende_en_institucion = forms.ChoiceField(
        choices=[("True", "Sí"), ("False", "No")],
        widget=forms.RadioSelect
    )

    class Meta:
        model = Emprendimiento
        exclude = ("usuario", "estado", "fecha_envio")

        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
            "fecha_creacion": forms.DateInput(attrs={"type": "date"}),
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "categoria": forms.Select(),
        }

    # =========================
    # LIMPIEZA DE DATOS
    # =========================

    def clean_metodo_pago(self):
        data = self.cleaned_data["metodo_pago"]
        return ",".join(data)  # guarda como string

    def clean_es_estatico(self):
        return self.cleaned_data["es_estatico"] == "True"

    def clean_tiene_domicilio(self):
        return self.cleaned_data["tiene_domicilio"] == "True"

    def clean_es_estudiante(self):
        return self.cleaned_data["es_estudiante"] == "True"

    def clean_vende_en_institucion(self):
        return self.cleaned_data["vende_en_institucion"] == "True"
    



# =========================
# PRODUCTOS
# =========================

class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = [
            "nombre",
            "descripcion",
            "precio",
            "imagen",
            "categoria",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={
                "placeholder": "Nombre del producto"
            }),

            "descripcion": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Descripción del producto"
            }),

            "precio": forms.NumberInput(attrs={
                "placeholder": "Precio"
            }),

            "categoria": forms.Select(),

            "imagen": forms.FileInput(attrs={
                "hidden": True
            }),
        }