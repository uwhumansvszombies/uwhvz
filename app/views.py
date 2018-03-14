from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse


def index(request):
    return render(request, 'index.html')


@login_required
def dashboard(request):
    return HttpResponse(f'Hello {request.user.username}')
