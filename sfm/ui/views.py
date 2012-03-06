from django.shortcuts import render

from ui.models import Status

def home(request):
    return render(request, 'home.html', {
        'title': 'home',
        'statuses': Status.objects.all(),
        })
