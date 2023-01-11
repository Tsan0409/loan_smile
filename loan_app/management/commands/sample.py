from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "テストコマンド"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Successfully create todo'))
