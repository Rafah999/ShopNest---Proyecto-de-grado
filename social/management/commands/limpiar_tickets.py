from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from social.models import SolicitudContacto


class Command(BaseCommand):
    help = "Elimina tickets cerrados con más de 24 horas"

    def handle(self, *args, **kwargs):
        limite = timezone.now() - timedelta(hours=24)

        eliminados, _ = SolicitudContacto.objects.filter(
            estado="cerrada",
            fecha__lt=limite
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Se eliminaron {eliminados} registros."
            )
        )