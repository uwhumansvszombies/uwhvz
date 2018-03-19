def is_moderator(user):
    if user.groups.filter(name='moderator').count() > 0:
        return True
    return False
