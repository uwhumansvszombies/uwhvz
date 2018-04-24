from django.contrib.auth.decorators import user_passes_test, REDIRECT_FIELD_NAME


def moderator_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    def _is_moderator(user):
        return user.is_authenticated and user.is_moderator()

    actual_decorator = user_passes_test(_is_moderator, login_url=login_url, redirect_field_name=redirect_field_name)
    if function:
        return actual_decorator(function)
    return actual_decorator
