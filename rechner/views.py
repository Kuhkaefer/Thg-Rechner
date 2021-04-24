from django.shortcuts import render, get_object_or_404, get_list_or_404  
from django.forms import inlineformset_factory
from .models import EventTemplate, Question, DefaultAmounts, Category
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
    dfs = event_template.defaultamounts_set.all()
    questions = []
    for df in dfs:
        questions.append(df.question)
    
    # sort by category
    def sort_f(q):
        return q.category.id
    questions.sort(key=sort_f)
    
    # get defaults and list with 1, if question category is new
    defaults = []
    old_cat = ""
    first_in_cat = np.zeros(len(questions), dtype=bool)
    last_in_cat = np.zeros(len(questions), dtype=bool)
    for i,q in enumerate(questions):
        defaults.append(dfs.get(question=q).value)
        # mark first question of category
        if old_cat != q.category:
            first_in_cat[i] = True
            # mark last question of category
            if i>0:
                last_in_cat[i-1] = True
            old_cat = q.category
    last_in_cat[i] = True
    print(last_in_cat)
            
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
    
    # Get categories
    categories = Category.objects.all()
    
    # Get all question as list:
    q_list = [None]*Question.objects.all().count()
    for i,q in enumerate(Question.objects.all()):
       q_list[i] =q
    
    
    # Create context
    context = {
        'template_instance':event_template,
        'q_d_f_and_l':zip(questions,defaults,first_in_cat, last_in_cat),
        'page_name':f"CO2 bei {event_template.name}",
        'page_header':f"Event: {event_template.name}",
        'button_link':'/rechner',
        'categories':categories,
        'q_list':q_list,
    }
    
    # Render Form
    return render(request, 'rechner/show_simple_form.html', context)
