from django.core.management.base import BaseCommand

from datetime import datetime

from app.models import Game, Tag, PlayerRole, TagType


class Command(BaseCommand):
    help = 'Converts old tree types to the new tag system'

    def handle(self, *args, **options):
        games = Game.objects.all().filter(active=True,started_on__lte=datetime(2019,12,31)) #every game before 2020
        
        for game in games:
            tags = Tag.objects.filter(
                initiator__game=game,
                receiver__game=game,
                initiator__role=PlayerRole.ZOMBIE,
                receiver__role=PlayerRole.HUMAN,                
                active=True)
            
            for tag in tags:
                tag.type=TagType.KILL
                tag.save()
