from django.urls import path
from . import views

urlpatterns = [

    path(
        "seguir/<int:emprendimiento_id>/",
        views.toggle_seguimiento,
        name="toggle_seguimiento"
    ),

]