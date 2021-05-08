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
    
## Helper functions
    def save_user_input(request, defaults,new_d_list,new_q_id_list):  
        
        #print(f"keys: {request.POST.keys()}")
        #print(f"4: {request.POST.get('4')}")
        
        # get user input for template questions
        for i,q in enumerate(questions):
            defaults[i] = request.POST.get(str(q.pk))
            
        # get user input for new questions
        for i,qid in enumerate(new_q_id_list):
            #print(f"qid: ")
            #print(qid)
            new_d_list[i] = request.POST.get(str(int(qid)))
            
        #print("new_d_list")
        #print(new_d_list)
        
        # Save user_input as session
        request.session['user_input'] = defaults
        request.session['user_input_new_q'] = new_d_list
        
        return request, defaults
    
## Preparation
    # Get chosen Template and related questions
    event_template = get_object_or_404(EventTemplate, pk=template_id) 
    request.session['event_template'] = event_template.pk
    dfs = event_template.defaultamounts_set.all()
    questions = []
    for df in dfs:
        questions.append(df.question)
    
    # sort by category
    def sort_f(q):
        return q.category.id
    questions.sort(key=sort_f)
    
    # get defaults and list with info, wether question is first or last in category
    defaults = []
    old_cat = ""
    first_in_cat = np.zeros(len(questions), dtype=bool)
    last_in_cat = np.zeros(len(questions), dtype=bool)
    existing_cats = []
    for i,q in enumerate(questions):
        defaults.append(dfs.get(question=q).value)
        # mark first question of category
        if old_cat != q.category:
            existing_cats.append(q.category)
            first_in_cat[i] = True
            # mark last question of category
            if i>0:
                last_in_cat[i-1] = True
            old_cat = q.category
    last_in_cat[i] = True
    
    # get missing categories
    all_cats = Category.objects.all()
    missing_cats = []
    for c in all_cats:
        if c not in existing_cats:
            missing_cats.append(c)
    
            
## Check user input            

    # User submitted the form
    if (request.method == "POST"):
    
        # get previous new_question and defalist
        new_q_id_list = request.session['new_q_id_list'] 
        new_d_list = request.session['user_input_new_q'] 
            
        # save user input in question fields
        request, defaults = save_user_input(request, defaults,new_d_list,new_q_id_list)
    
        # Check if user added field
        added_field_qid = max(list(map(float,request.POST.getlist("new_field"))))
        
        # User added field
        if added_field_qid >= 0:
            
            print(f"field added. With question {added_field_qid}")
            
            # update new_question list
            new_q_id_list.append(added_field_qid)
            request.session['new_q_id_list'] = new_q_id_list
            new_d_list.append("0")
            request.session['user_input_new_q']  = new_d_list
            
            #print(f"new q id list: {new_q_id_list}")
            
        # User pressed "submit" button
        elif request.POST.get("submit"):
            
            print("submit")
                
            # Move on to next page
            return HttpResponseRedirect('/rechner/result')
    
        # User did something stupid
        else:
            print('no field added')
            print("useless")
            print(request.POST.getlist("new_field"))
            
        
    # First Request of this page (Blank, unbinded Page, if so with default values)
    elif (request.method == "GET"):
        print("first")
        # reset added questions and user input
        request.session['new_q_id_list'] = []
        request.session['user_input_new_q'] = []
        request.session['user_input'] = []

## Handle User Input
    # get new question and default list from new question id's
    new_q_list = []
    for id in request.session['new_q_id_list']:
        new_q_list.append(Question.objects.get(pk=id))

    
    # Get all (not yet existing) new questions as list:
    q_list = [None]*Question.objects.all().count()
    for i,q in enumerate(Question.objects.all()):
        if q not in questions and q not in new_q_list:  
            q_list[i] =q  
            
    # Get answer to new questions
    new_d_list = request.session['user_input_new_q'] 
       
    # Create context
    context = {
        'template_instance':event_template,
        'q_d_f_and_l':zip(questions,defaults,first_in_cat, last_in_cat),
        'page_name':f"CO2 bei {event_template.name}",
        'page_header':f"Event: {event_template.name}",
        'button_link':'/rechner',
        'q_list':q_list,
        'new_q_d_list':np.array([new_q_list,new_d_list]).T.tolist(),
        'missing_cats': missing_cats,
    }
    
    # Render Form
    return render(request, 'rechner/show_simple_form.html', context)
