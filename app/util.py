def is_moderator(user):
    if user.groups.filter(name='Moderator').count() > 0 or user.is_superuser:
        return True
    return False
