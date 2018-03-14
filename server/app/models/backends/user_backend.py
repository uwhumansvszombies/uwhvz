from django.contrib.auth.backends import ModelBackend

from app.models import User


class UserModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = self._get_user_by_email_or_username(username)
        except User.DoesNotExist:
            # Run the password hasher once to reduce the timing difference
            # between an existing and a nonexistent user.
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    @staticmethod
    def _get_user_by_email_or_username(identifier):
        if '@' in identifier:
            return User.objects.get(email=identifier)
        else:
            return User.objects.get(username=identifier)
