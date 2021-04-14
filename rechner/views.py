from django.shortcuts import render, get_object_or_404, get_list_or_404  
from django.forms import inlineformset_factory
from .models import EventTemplate, Question, DefaultAmounts
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from rechner.forms import FillEvent

## Index Seite
def index(request):
    print("back on rechner index")
    
    page_text = f"Wait for it.\nChoose an event template"
    
    # If button clicked (I think)
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
       
    else:
        choice=""
    
    context = {
        'page_name':'CO2 Rechner',
        'page_header':'CO2 Rechner',
        'page_text':page_text,
        'event_templates':EventTemplate.objects.all(),
        'button_link':'/rechner',
        'button_text':'Go!'
        }
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
    
    event_template = get_object_or_404(EventTemplate, pk=template_id) 
    questions = event_template.questions.all()
    
    print(questions[0].question_text)
    
    defaults = []
    for q in questions:
        print(q.name)
        defaults.append(DefaultAmounts.objects.all().filter(template=event_template,question=q)[0].value)

        # NOT the first request of the page (user populated fields. Form is bound to user.)
    if request.method == "POST":
        
        first = False
        
        for i,q in enumerate(questions):
            print(f"your answer for {q.name}: {request.POST.get(q.name)}")
            defaults[i] = request.POST.get(q.name)
        
        request.session['user_input'] = defaults
            
        return HttpResponseRedirect('/rechner/result')
    
    # First Request of this page (Blank, unbinded Page, if so with default values)
    else:
        first = True
    
    context = {
        'template_instance':event_template,
        'q_and_d':zip(questions,defaults),
        'page_name':f"CO2 bei {event_template.name}",
        'page_header':f"Event: {event_template.name}"
    }
    
    # Return some render
    return render(request, 'rechner/show_simple_form.html', context)
