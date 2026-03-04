from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Emprendimiento


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

    # 🔥 Booleanos como SÍ / NO
    es_estatico = forms.ChoiceField(
        choices=[(True, "Sí"), (False, "No")],
        widget=forms.RadioSelect
    )

    tiene_domicilio = forms.ChoiceField(
        choices=[(True, "Sí"), (False, "No")],
        widget=forms.RadioSelect
    )

    es_estudiante = forms.ChoiceField(
        choices=[(True, "Sí"), (False, "No")],
        widget=forms.RadioSelect
    )

    vende_en_institucion = forms.ChoiceField(
        choices=[(True, "Sí"), (False, "No")],
        widget=forms.RadioSelect
    )

    class Meta:
        model = Emprendimiento
        exclude = ("usuario", "estado", "fecha_envio")
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
            "fecha_creacion": forms.DateInput(attrs={"type": "date"}),
            "descripcion": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_es_estatico(self):
        return self.cleaned_data["es_estatico"] == "True"

    def clean_tiene_domicilio(self):
        return self.cleaned_data["tiene_domicilio"] == "True"

    def clean_es_estudiante(self):
        return self.cleaned_data["es_estudiante"] == "True"

    def clean_vende_en_institucion(self):
        return self.cleaned_data["vende_en_institucion"] == "True"
