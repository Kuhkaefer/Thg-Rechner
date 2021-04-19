from django.shortcuts import render, get_object_or_404, get_list_or_404  
from django.forms import inlineformset_factory
from .models import EventTemplate, Question, DefaultAmounts
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import numpy as np

from rechner.forms import FillEvent

## Index Seite
def index(request):
    
    page_text = f"Choose an event template"
    
    # Check choice, If button clicked (I think)
    if request.method == "POST":
       choice= request.POST.get('chosen_template')
       print(len(choice))
       if choice is "":
           choice = "/rechner"
           print(choice)
           page_text += '. WRONG CHOICE'
           print("wrong choice")
       else:       
           return HttpResponseRedirect(f'{choice}')
       
    # If first call of page   
    else:
        choice=""
    
    # create context
    context = {
        'page_name':'CO2 Rechner',
        'page_header':'CO2 Rechner',
        'page_text':page_text,
        'event_templates':EventTemplate.objects.all(),
        'button_link':'/rechner',
        'button_text':'Go!'
        }
    
    # render context into page
    return render(request,'rechner/choose_eventtemplate.html',context)

## Ergebnis Seite
def result(request):
    context = {
        'page_name':'CO2 Result',
        'page_header':'CO2 Result',
        'page_description': f'discombobulated combobulator. { request.session["user_input"] }'
        }
    
    return render(request, 'rechner/simple_page.html', context)
    

## Abfrage-Seite
def fill_event_template(request, template_id):
    
    # Get chosen Template and related questions
    event_template = get_object_or_404(EventTemplate, pk=template_id) 
    questions = event_template.questions.all().order_by('category')
    
    # get defaults and list with 1, if question category is new
    defaults = []
    old_cat = ""
    new_cat = np.zeros(len(questions))
    for i,q in enumerate(questions):
        defaults.append(DefaultAmounts.objects.all().filter(template=event_template,question=q)[0].value)
        if old_cat != q.category:
            new_cat[i] = 1
            old_cat = q.category
            
    # NOT the first request of the page (user populated fields. Form is bound to user.)
    if request.method == "POST":
        
        # get user input
        user_input = defaults
        for i,q in enumerate(questions):
            user_input[i] = request.POST.get(q.name)
        
        # Save user_input as session
        request.session['user_input'] = user_input
            
        # Move on to next page
        return HttpResponseRedirect('/rechner/result')
    
    # First Request of this page (Blank, unbinded Page, if so with default values)
    else:
        pass
    
    # Create context
    context = {
        'template_instance':event_template,
        'q_and_d':zip(questions,defaults,new_cat),
        'page_name':f"CO2 bei {event_template.name}",
        'page_header':f"Event: {event_template.name}",
    }
    
    # Render Form
    return render(request, 'rechner/show_simple_form.html', context)
