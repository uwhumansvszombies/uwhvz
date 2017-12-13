from django.shortcuts import render


def index(request):
    return render(request, 'index.html')

def dashboard(request):
    if (request.user.is_authenticated):
        return render(request, 'dashboard/dashboard.html')
    else:
        return render(request, 'registration/login.html')
