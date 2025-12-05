from django.core.management.base import BaseCommand

# PUBLIC_INTERFACE
class Command(BaseCommand):
    """
    Simple healthcheck command for system orchestration and health reporting.
    Does NOT check database connectivity (only returns 0 if Django is importable/running).
    """
    help = "Return a 0 exit code if Django app is importable and running. Does not check DB."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Django application importable and management command executed. (No DB check performed)"))
