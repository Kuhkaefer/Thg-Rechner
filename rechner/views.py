from django.shortcuts import render
from django.forms import inlineformset_factory

## Abfrage-Seite
def fill_event_template(request, template_id):
    
    # Get requested event template
    event_template = EventTemplate.objects.get(pk=template_id)
    
    # Get Inline Formset (form that takes field from all Questions related to eventTemplate )
    EvTempInlineFormSet = inlineformset_factory(EventTemplate, Question, fields='question_text')
    
    # NOT the forst request of the page (user populated fields. Form is bound to user.)
    if request.method == "POST":
        # create an instance of the form and populated it with the user data
        formset = BookInlineFormSet(request.POST, instance=event_template)
        
        # do something (validation of user input, ...)
        
        # return something
        return HttpResponseRedirect(KEINE_AHNUNG)
    
    # First Request of this page (Blank, unbinded Page, if so with default values)
    else:
        # create an instance of the form and populated it with default data
        formset = BookInlineFormSet(initial={"Feld":"irgendwie defaults und so"}, instance=event_template) 
    
    # Return some render
    return render(request, 'TOLLES_TEMPLATE.html', {'formset': formset})
