from django.shortcuts import render
from django.forms import inlineformset_factory
from .models import EventTemplate, Question
from django.http import HttpResponse
from django.http import HttpResponseRedirect

## Index Seite
def index(request):
    return HttpResponse(f"Hello, world. You're at the rechner index.")


## Abfrage-Seite
def fill_event_template(request, template_id):
    
    # Get requested event template
    event_template = EventTemplate.objects.get(pk=template_id)
    
    # Get Inline Formset (form that takes field from all Questions related to eventTemplate )
    print("lel")
    EvTempInlineFormSet = inlineformset_factory(EventTemplate, Question.event_template.through, fields=('question_text',))
    print("lol")
    
    # NOT the forst request of the page (user populated fields. Form is bound to user.)
    if request.method == "POST":
        # create an instance of the form and populated it with the user data
        formset = EvTempInlineFormSet(request.POST, instance=event_template)
        
        # do something (validation of user input, ...)
        
        # return something
        return HttpResponseRedirect('/index')
    
    # First Request of this page (Blank, unbinded Page, if so with default values)
    else:
        # create an instance of the form and populated it with default data
        formset = EvTempInlineFormSet(initial={"Feld":"irgendwie defaults und so"}, instance=event_template) 
    
    # Return some render
    #return render(request, 'TOLLES_TEMPLATE.html', {'formset': formset})
    return HttpResponse("You're on template %s." % template_id)
