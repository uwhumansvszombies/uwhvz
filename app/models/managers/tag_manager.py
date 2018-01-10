from django.db import models


class TagManager(models.Manager):
    def create_tag(self, initiator, receiver, tagged_at, location, description):
        if initiator.role == receiver.role:
            raise ValueError('A tag must be between opposite teams')

        tag = self.model(
            initiator=initiator,
            receiver=receiver,
            tagged_at=tagged_at,
            location=location,
            description=description,
        )
        tag.save(using=self._db)
        return tag
