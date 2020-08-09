from django.core.management.base import BaseCommand

from datetime import datetime

from app.models import Game, Tag, PlayerRole, TagType


class Command(BaseCommand):
    help = 'Converts old OZ tags to the new tag system'

    def handle(self, *args, **options):
        games = Game.objects.all().filter(started_on__lte=datetime(2019,12,31)) #every game before 2020
        
        for game in games:
            ozs = Player.objects.filter(
                in_oz_pool=True,
                game=game)
            
            for oz in ozs:
                oz.is_oz=True
                oz.save()
