def is_moderator(user):
    if user.groups.filter(name='Moderator').count() > 0:
        return True
    return False
