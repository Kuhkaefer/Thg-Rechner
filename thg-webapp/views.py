
from django.http import HttpResponse


def home(request):
    return HttpResponse(f"Home Page. Look around. Nice and homely here. Soothing. Welcome. ")
