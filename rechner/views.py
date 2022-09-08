from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.forms import inlineformset_factory
from .models import EventTemplate, Question, DefaultAmounts, Category
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from rechner import helpers as H
from rechner import constants as C

from rechner.forms import FillEvent

## Index Seite
def index(request):
    page_text = f"Wähle ein Veranstaltungsformat als Vorlage:"

    # Check template choice, If button clicked (I think)
    if request.method == "POST":
       choice = request.POST.get('chosen_template')
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
        'button_text':'Los!'
        }

    # render context into page
    return render(request,'rechner/choose_eventtemplate.html',context)

## Ergebnis Seite
def result(request):
    # Chosen Event-Template
    event_template = request.session['event_template_id']

    # Array with users answers to questions of event template
    user_data = np.array(request.session["user_data"])

    ## Calculate Emissions (total & per category)

    # Preparation
    sum_per_e = 0
    sum_per_c_dict = {}

    # Loop through questions
    for entry in user_data:

        # get stuff
        question = get_object_or_404(Question, pk=entry[C.iQ])
        category = get_object_or_404(Category, pk=entry[C.iC])
        user_value = entry[C.iV]

        # reset emission per category
        if entry[C.iF]:
            sum_per_c = 0

        # emission per question
        sum_per_q = 0
        for emi in question.emissions.all():
            sum_per_q += float(emi.value)
        sum_per_q *= user_value

        # add to emission per category
        sum_per_c += sum_per_q

        # total emission per category
        if entry[C.iL]:
            sum_per_c_dict[category.name] = sum_per_c

        # add to emission per event
        sum_per_e += sum_per_q

    print(sum_per_e)
    print(sum_per_c_dict)
    c_values = pd.DataFrame(sum_per_c_dict)


    context = {
        'page_name':'CO2 Result',
        'page_header':'CO2 Result',
        'page_description': f'discombobulated combobulator.\n {user_data[:,C.iV]}',
        'page_content' : f'Total emissions: {sum_per_e} Mio t CO2eq.',
        }

    return render(request, 'rechner/simple_page.html', context)


## Abfrage-Seite
def fill_event_template(request, template_id):
    ## Always 1

    # event template
    event_template = get_object_or_404(EventTemplate, pk=template_id)

    # submitting ok?
    can_submit = True
    reset      = False


    ## Resetting
    print(request.POST.get('reset'))
    if (request.method == "POST") & (request.POST.get('reset')=='Reset'):
        reset = True
        print("reset")

    ## First Call
    if (request.method == "GET") or reset:
        ## Initialize values
        print("first")
        print(request.GET.get('remove_field'))
        # template questions list and defaults as values list
        def_amnts = event_template.defaultamounts_set.all()
        data  = np.zeros((len(def_amnts), C.columns))
        for i,df in enumerate(def_amnts):
            data[i,C.iQ] = df.question.pk
            data[i,C.iV] = df.value
            data[i,C.iC] = df.question.category.pk
            data[i,C.iO] = i

        # sort by category and Order
        idx = np.lexsort((data[:,C.iO],data[:,C.iC]))
        data = data[idx]

        # get first and last bools
        data = H.get_first_and_last(data)

        # Non relevant quantites
        added_cat = None
        new_c_q_list = None


    ## Later Call
    elif request.method == "POST":
        print("POST")
        ## Read session
        data = np.array(request.session['user_data'])

        ## Read user input

        # Read entered values
        for i,q in enumerate(data[:,C.iQ]):
            ui = request.POST.get(str(int(q)))

            #try float(ui):
            try:
                data[i,C.iV] = ui
            except:
                data[i,C.iV] = 0
                can_submit=False

        # Read added fields
        if request.POST.get('add_field') != None:
            added_field_qid = max(list(map(float,request.POST.getlist("new_field"))))

            # User did add field
            if added_field_qid >= 0:
                print("Added field")
                row = np.zeros(data[0].shape)
                row[C.iQ] = added_field_qid
                row[C.iC] = get_object_or_404(Question, pk=added_field_qid).category.pk
                row[C.iO] = np.max(data[:,C.iO])+1
                data = np.vstack([data,row])

                # Sort data again
                idx = np.lexsort((data[:,C.iO],data[:,C.iC]))
                data = data[idx]

                # Update first and last bools
                data = H.get_first_and_last(data)

        # Read added Category
        if request.POST.get('add_cat')!=None:
            print("Added Category")
            added_cat_id = max(list(map(float,request.POST.getlist("new_cat"))))
            if (added_cat_id >= 0):
                added_cat = get_object_or_404(Category,pk=added_cat_id)
                new_c_q_list = Question.objects.filter(category = added_cat)
            else:
                added_cat = None
                new_c_q_list = None
        else:
            added_cat = None
            new_c_q_list = None

        # Read deleted field and delete it
        if request.POST.get('remove_field')!=None:
            print("Removed field")
            data = np.delete(data, obj=np.argwhere(data[:,C.iQ]==float(request.POST.get('remove_field'))),axis=0)

            # Update first and last bools
            data = H.get_first_and_last(data)


        ## Process User input

        # User pressed enter key
        if request.POST.get("enter"):
            print("enter")

            # save entered values
            request.session['user_data'] = data.tolist()

            if can_submit:
                # Move on to next page
                return HttpResponseRedirect('/rechner/result')
            else:
                pass


        # User pressed "submit" button
        if request.POST.get("submit form"):
            print("submit")

            # save entered values
            request.session['user_data'] = data.tolist()

            if can_submit:
                # Move on to next page
                return HttpResponseRedirect('/rechner/result')
            else:
                pass


    ## Always

    # get missing qs and cats
    missing_qs, missing_cats = H.get_missing(data)

    ## Save data
    request.session['event_template_id'] = template_id
    request.session['user_data'] = data.tolist()

    ## DEbug

    print(data)


    ## Create context

    # Get model objects from IDs in numpy array
    q_list = []
    for qid in data[:,C.iQ]:
        q_list.append(get_object_or_404(Question, pk=qid))

    misscats_list = []
    for mcid in missing_cats:
        misscats_list.append(get_object_or_404(Category, pk=mcid))

    missqs_list = []
    for mqid in missing_qs:
        missqs_list.append(get_object_or_404(Question, pk=mqid))

    # create context dict
    context = {
        'template_instance':event_template,
        'q_v_f_and_l':zip(q_list,data[:,C.iV],data[:,C.iF],data[:,C.iL]),
        'missing_qs':missqs_list,
        'missing_cats': misscats_list,
        'cat_added':added_cat,
        'new_c_q_list':new_c_q_list,
        'page_name':f"CO2 bei {event_template.name}",
        'page_header':f"Veranstaltung: {event_template.name}",
        'page_description':'Bitte trage die Menge der verschiedenen Posten ein:',
        'button_link':'/rechner',
    }

    # Render Form
    return render(request, 'rechner/show_noform.html', context)
