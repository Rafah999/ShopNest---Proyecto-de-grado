from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from usuarios.models import *
from .models import *

@login_required
def toggle_seguimiento(request, emprendimiento_id):

    emprendimiento = Emprendimiento.objects.get(
        id=emprendimiento_id
    )

    seguimiento = Seguimiento.objects.filter(
        usuario=request.user,
        emprendimiento=emprendimiento
    )

    if seguimiento.exists():

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

    return JsonResponse({

        "success": True,

        "siguiendo": siguiendo,

        "total_seguidores": total_seguidores

    })