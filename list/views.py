from django.shortcuts import render

# Create your views here.
from list.models import Emission, Kategorie, Frage

def index(request):
    """View function for home page of site."""

    num_emissions = Emission.objects.all().count()

    context = {
        'num_emissions': num_emissions,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)
