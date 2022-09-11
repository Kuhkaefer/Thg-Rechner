from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import EventTemplate, Question, DefaultAmount, Category, CalculationFactor
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import plot
from rechner import helpers as H
from rechner import constants as C

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
    result_df = pd.DataFrame(columns=["Produkt", "Feld", "Kategorie", \
                                "Menge", "Einheit", "CO2/St.","CO2 gesamt", "Anmerkung"])
    i = 0

    # Loop through questions
    for entry in user_data:

        # get stuff
        question = get_object_or_404(Question, pk=entry[C.iQ])
        category = get_object_or_404(Category, pk=entry[C.iC])
        user_value = entry[C.iV]

        # emission per question
        for cf in question.calculationfactor_set.all():
            emi = cf.emission

            result_df.loc[i,"Produkt"] = emi.name
            result_df.loc[i,"Feld"] = question.name
            result_df.loc[i,"Kategorie"] = question.category.name
            result_df.loc[i,"Einheit"] = emi.unit
            result_df.loc[i,"Anmerkung"] = emi.explanation

            # Check units
            if question.unit != emi.unit:
                raise Exception(f"Unit Mismatch!: \"{question.name}\" expects {question.unit}, wheras \"{emi.name}\" requires {emi.unit}.")

            # get amount
            if cf.fixed:
                result_df.loc[i,"Menge"] = float(cf.factor)
            else:
                result_df.loc[i,"Menge"] = float(cf.factor)*user_value

            # get emission per unit & consider emission factors
            result_df.loc[i,"CO2/St."] =  float(emi.value)
            for emission_factor in emi.factor.all():
                result_df.loc[i,"CO2/St."] *= float(emission_factor.value)

            # multiply with amount and add to questions emission
            result_df.loc[i,"CO2 gesamt"] = result_df.loc[i,"CO2/St."]  * result_df.loc[i,"Menge"]

            # raise counter
            i += 1

    # cleanup
    del i

    # get CO2 sum per unique entry in column "col"
    def sum_per(col, drop_zero=True, on_col="CO2 gesamt", reset_index=True, sort=False, sort_on=None):
        if sort_on is None:
            sort_on = on_col

        out = pd.DataFrame(result_df.groupby(col)[on_col].sum())

        if drop_zero:
            out= out.loc[out[on_col]!=0,:]

        if reset_index:
            out.reset_index(inplace=True)

        if sort:
            out.sort_values(sort_on, ascending=False, inplace=True)

        return out

    ## Create output table
    # df with CO2 sum per question, sorted in descending order by CO2 gesamt:
    # table = sum_per("Feld", reset_index=False, sort=True)

    # df with CO2 per Emission, sorted in descending order by CO2 gesamt:
    table = result_df.sort_values("CO2 gesamt", ascending=False)

    ## Plot result
    fig = go.Figure(px.pie(sum_per("Kategorie"), names="Kategorie", values="CO2 gesamt", color="Kategorie", width=800, height=400))#, color="category name", text="category name"))
    plt_div = plot(fig, output_type='div')

    context = {
        'page_name':'CO2 Result',
        'page_header':'CO2 Result',
        'page_description': f'discombobulated combobulator.\n ',
        'table' : table.to_html(),
        'co2_sum' : result_df.loc[:,"CO2 gesamt"].sum().round(3),
        'plot':plt_div,
        }

    return render(request, 'rechner/plot.html', context)


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
        def_amnts = event_template.defaultamount_set.all()
        data  = np.zeros((len(def_amnts), C.columns))
        for i,df in enumerate(def_amnts):
            data[i,C.iQ] = df.question.pk
            data[i,C.iV] = df.value
            data[i,C.iC] = df.question.category.pk
            data[i,C.iU] = False if df.question.unit in ["", " "] else True
            data[i,C.iI] = False if df.question.info_text in ["", " "] else True
            data[i,C.iO] = i
            print(df.question.name)
            print(f"-{df.question.unit}-")
            print(data[i,C.iU])
        del i

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
        for j,q in enumerate(data[:,C.iQ]):
            ui = request.POST.get(str(int(q)))

            #try float(ui):
            try:
                data[j,C.iV] = eval(ui)
            except:
                data[j,C.iV] = None
                can_submit=False
        del j

        # Read added fields
        if request.POST.get('add_field') != None:
            added_field_qid = max(list(map(float,request.POST.getlist("new_field"))))

            # User did add field
            if added_field_qid >= 0:
                q = get_object_or_404(Question, pk=added_field_qid)
                row = np.zeros(data[0].shape)
                row[C.iQ] = added_field_qid
                row[C.iC] = q.category.pk
                row[C.iO] = np.max(data[:,C.iO])+1
                row[C.iU] = False if q.unit in ["", " "] else True
                row[C.iI] = False if q.info_text in ["", " "] else True
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
        'q_v_f_l_u_and_i':zip(q_list,data[:,C.iV],data[:,C.iF],data[:,C.iL],data[:,C.iU],data[:,C.iI]),
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
    return render(request, 'rechner/fill_eventtemplate.html', context)

def base(request):
    return render(request, 'rechner/base.html',{"page_header":"jo"})
