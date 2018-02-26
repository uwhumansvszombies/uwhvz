from django.http import JsonResponse
from django.core.serializers import serialize
from .models import User


def my_view(request):
    user = User.objects.first()
    user_json = {
        'username': user.username,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'email': user.email,
    }
    return JsonResponse(user_json)


# [{"model": "app.user", "pk": "d06cec65-e378-439a-a6d3-ef53b910e8b1", 
# "fields": {
#     "password": "argon2$argon2i$v=19$m=512,t=2,p=2$b09DWWJpaDY2cWJj$BhdBNycV3+KQc7jd+d8Y0A",
#     "last_login": "2018-02-25T18:39:13.028Z",
#     "is_superuser": true,
#     "is_staff": true,
#     "is_active": true,
#     "date_joined": "2018-02-25T18:08:18.279Z",
#     "username": "tristan",
#     "first_name": "Tristan",
#     "last_name": "Ohlson",
#     "email": "tsohlson@gmail.com",
#     "groups": [],
#     "user_permissions": []}}]