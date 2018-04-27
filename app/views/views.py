from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard/index.html')


@login_required
def report_tag(request):
    if request.method == 'POST':
        # Find the player using the code from the request
        # Do the tag using TagManager
        # Report any errors if there are any
        messages.add_message(request, messages.ERROR, "There was an error reporting a tag:")
        # Report success if it worked!

    return render(request, 'dashboard/index.html')
