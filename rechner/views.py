from django.shortcuts import render, get_object_or_404  
from django.forms import inlineformset_factory
from .models import EventTemplate, Question
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from rechner.forms import FillEvent

## Index Seite
def index(request):
    return HttpResponse(f"Hello, world. You're at the rechner index.")


## Abfrage-Seite
def fill_event_template(request, template_id):
    
    event_template = get_object_or_404(EventTemplate, pk=template_id) 
    
    # NOT the forst request of the page (user populated fields. Form is bound to user.)
    if request.method == "POST":
        # create an instance of the form and populated it with the user data
        form = FillEvent(request.POST)
        
        # do something (validation of user input, ...)
        if form.is_valid():
            print(form.cleaned_data['number'])
        
        # return something
        return HttpResponseRedirect('/rechner')
    
    # First Request of this page (Blank, unbinded Page, if so with default values)
    else:
        # create an instance of the form and populated it with default data
        form = FillEvent() 
        
    
    context = {
        'form': form,
        'template_instance':event_template
    }
    
    # Return some render
    #return render(request, 'TOLLES_TEMPLATE.html', {'formset': formset})
    return render(request, 'rechner/show_simple_form.html', context)
