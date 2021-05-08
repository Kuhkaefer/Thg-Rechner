from django.shortcuts import render, get_object_or_404, get_list_or_404  
from django.forms import inlineformset_factory
from .models import EventTemplate, Question, DefaultAmounts, Category
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import numpy as np
from rechner import helpers as H
from rechner import constants as C

from rechner.forms import FillEvent

## Index Seite
def index(request):
    page_text = f"Choose an event template"
    
    # Check template choice, If button clicked (I think)
    if request.method == "POST":
       choice= request.POST.get('chosen_template')
       if choice == "":
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
    # Chosen Event-Template
    event_template = request.session['event_template']
    
    # Array with users answers to questions of event template
    answers = request.session["user_input"]
    
    #  Array with new IDs of questions added by user
    new_q_id_list = request.session['new_q_id_list'] 
    
    # Array with users answers to new (added) questions
    answers_new_q = request.session["user_input_new_q"]
    
    
    context = {
        'page_name':'CO2 Result',
        'page_header':'CO2 Result',
        'page_description': f'discombobulated combobulator. { [request.session["user_input"],request.session["user_input_new_q"]] }'
        }
    
    return render(request, 'rechner/simple_page.html', context)
    

## Abfrage-Seite
def fill_event_template(request, template_id):
    
    # First Call
    if (request.method == "GET"):
        
        # Initialize values

        # event template
        event_template = get_object_or_404(EventTemplate, pk=template_id) 
        request.session['event_template_id'] = event_template.pk

        # template questions list and defaults as values list
        def_amnts = event_template.defaultamounts_set.all()
        data  = np.zeros((len(def_amnts), C.columns))
        for i,df in enumerate(def_amnts):
            data[i,C.iQ] = df.question.pk
            data[i,C.iV] = df.value
            data[i,C.iC] = df.question.category.pk
            
        # sort by category
        data = data[data[:, C.iC].argsort()]
            
        # get first and last bools
        data = H.get_first_and_last(data)
    
    
    # Create context
    context = {
        'template_instance':event_template,
        'q_v_f_and_l':zip(data[:,C.iQ],data[:,C.iV],data[:,C.iF],data[:,C.iL]),
        'missing_qs':missing_qs,
        'missing_cats': missing_cats,
        'page_name':f"CO2 bei {event_template.name}",
        'page_header':f"Event: {event_template.name}",
        'button_link':'/rechner',
    }
    
    # Render Form
    return render(request, 'rechner/show_noform.html', context)
