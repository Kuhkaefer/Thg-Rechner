from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import EventTemplate, Question, DefaultAmount, Category, CalculationFactor, Advice
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
        user_value = entry[C.iV]

        # emission per question
        for cf in question.calculationfactor_set.all():

            # get miscellaneous
            emi = cf.emission
            result_df.loc[i,"Produkt"] = emi.name
            result_df.loc[i,"Feld"] = question.name
            result_df.loc[i,"Kategorie"] = question.category.name
            result_df.loc[i,"Einheit"] = emi.unit
            result_df.loc[i,"Anmerkung"] = emi.explanation

            # calculate emission
            result_df.loc[i,"CO2/St."], result_df.loc[i,"Menge"], result_df.loc[i,"CO2 gesamt"] = H.calc_co2(cf, user_value)

            # raise counter
            i += 1

    # cleanup
    del i, emi, question, user_value, entry

    ## Create Advice list

    # Preparation
    total_reduction = 0
    c = 0
    reduction_df = pd.DataFrame()

    # loop through advice
    for advice in Advice.objects.all():

        # check if question is part of user's input
        i = np.where(user_data[:,C.iQ]==advice.user_q.id)[0]

        if i.size>0:

            # get question index in user_data
            i = np.max(i)
            print(user_data[i,C.iV])

            # get idx of question in result_df
            idx = result_df[result_df.Feld==advice.user_q.name].index.values

            # get advice content
            has_new_q = True if np.any(advice.suggested_q) else False
            has_new_v = True if np.any(advice.suggested_v) else False
            has_text = True if hasattr(advice, "text") else False

            # Calculate Reduction Effect
            old_co2 = result_df.loc[result_df["Feld"]==advice.user_q.name,"CO2 gesamt"].sum()
            new_q = advice.suggested_q if has_new_q else advice.user_q
            new_v = advice.suggested_v if has_new_v else user_data[i,C.iV]
            new_co2 = 0
            for cf in new_q.calculationfactor_set.all():
                _,_,temp = H.calc_co2(cf,new_v)
                new_co2 += temp
            del temp
            reduction = new_co2-old_co2
            relative_reduction = reduction/result_df.loc[:,"CO2 gesamt"].sum()*100
            total_reduction += reduction
            print(old_co2)
            print(new_co2)

            # Create Advice string
            if len(advice.text)>0:
                advice_text = advice.text.format(
                    advice.user_q.name,
                    advice.suggested_q.name if has_new_q else None,
                    advice.suggested_v if has_new_v else None,
                    reduction,relative_reduction)
            else:
                # prepare advice text
                advice_text = ""

                # if different question suggested:
                if has_new_q:
                    advice_text +=  f"Ersetze '{advice.user_q.name}' mit '{advice.suggested_q.name}'. "

                # if different value suggested:
                if has_new_v:
                    if advice.suggested_v < user_data[i,iV]:
                        direction = "Reduziere"
                    else:
                        direction = "Erhöhe"
                    advice_text +=  f"{direction} auf {advice.suggested_v}. "

                # Result
                # advice_text +=  f"Resultat: {reduction:+.3f} kg ({relative_reduction:+.2f} %). "

            # save to result_df
            reduction_df.loc[c,"Option"] = advice_text
            reduction_df.loc[c,"Abs. Reduktion"] = reduction
            reduction_df.loc[c,"Rel. Gesamt-Reduktion"] = relative_reduction
            reduction_df.loc[c,"Feld"] = advice.user_q.name
            print(idx)
            reduction_df.loc[c,"Produkt-Nr."] = str(idx)
            c+=1

        # total relative reduction
        total_relative_reduction = total_reduction/result_df.loc[:,"CO2 gesamt"].sum()*100

    ## Create output table
    # df with CO2 sum per question ("Feld"), sorted in descending order by CO2 gesamt:
    # table = H.sum_per(result_df, "Feld", reset_index=False, sort=True)

    # df with CO2 per Emission, sorted in descending order by CO2 gesamt:
    table = result_df.sort_values("CO2 gesamt", ascending=False)

    ## Plot result
    fig = go.Figure(px.pie(H.sum_per(result_df, "Kategorie"), names="Kategorie",
                    values="CO2 gesamt", color="Kategorie", width=800, height=400))#, color="category name", text="category name"))
    plt_div = plot(fig, output_type='div')

    # Create output
    context = {
        'page_name':'CO2 Result',
        'page_header':'CO2 Result',
        'page_description': f'discombobulated combobulator.\n ',
        'table' : table.to_html(),
        'reduction_table' : reduction_df.to_html(),
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
