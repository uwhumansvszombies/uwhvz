from datetime import datetime, timedelta

from django.test import Client

from app.models import Player, Tag


class TagTester:
    """
    TagTester handles creation of tags in tests. It logs in as the initiator and reports
    a tag by POSTing to a fake server.
    """

    def __init__(self):
        self.client = Client()

    def tag(
        self,
        initiator: Player,
        receiver: Player,
        occurred_at: datetime,
        location: str = 'In a Test',
        description: str = 'I tagged them',
        password='password'
    ) -> Tag:
        self.client.login(username=initiator.user.email, password=password)
        self.client.post('/dashboard/report_tag', {
            'game': initiator.game.id,
            'player_code': receiver.code,
            'date': occurred_at.strftime('%Y-%m-%d'),
            'time': occurred_at.strftime('%H:%M%z'),
            'location': location,
            'description': description
        })

        return Tag.objects.get(
            initiator=initiator,
            receiver=receiver,
            tagged_at__range=(occurred_at - timedelta(seconds=61), occurred_at + timedelta(seconds=61))
        )
