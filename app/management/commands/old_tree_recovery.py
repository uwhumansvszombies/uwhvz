from django.core.management.base import BaseCommand

from datetime import datetime

from app.models import Game, Tag, PlayerRole, TagType


class Command(BaseCommand):
    help = 'Converts old tree types to the new tag system'

    def handle(self, *args, **options):
        games = Game.objects.all().filter(started_on__lte=datetime(2019,10,10)) #every game before 2021 Fall game
        
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
