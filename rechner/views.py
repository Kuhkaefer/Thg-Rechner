from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import EventTemplate, Question, DefaultAmount, Category, \
                    CalculationFactor, Advice, Source
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

    if request.method == "POST":

        # Check template choice and nu of ppl, If button clicked (I think)
        choice = request.POST.get('chosen_template')

        # no choice
        if choice == "":
            choice = "/rechner"

        # valid choice
        else:
            event_template = choice#request.session['event_template_id']

            # get number of participants
            if len(request.POST.get('nu_of_ppl')) > 0:
                nu_of_ppl = int(request.POST.get('nu_of_ppl'))
            else:
                ppl_id = Question.objects.filter(name='Teilnehmende')[0]
                try:
                    nu_of_ppl = float(DefaultAmount.objects.filter(question=ppl_id,template=event_template)[0].value)
                except:
                    nu_of_ppl = 1


            request.session['nu_of_ppl'] = nu_of_ppl
            return HttpResponseRedirect(f'event/{choice}')

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
    nu_of_ppl = int(float(request.session["nu_of_ppl"]))

    ## Calculate Emissions (total & per category)

    # Preparation
    result_df = pd.DataFrame()#columns=["Produkt", "Feld", "Kategorie", \
                                # "Menge", "Einheit", "CO2/St.","CO2 gesamt", "Anmerkung"])
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
            result_df.loc[i,"·TN"] = bool(entry[C.iS])
            result_df.loc[i,"Anmerkung"] = emi.explanation

            # calculate emission
            result_df.loc[i,"CO2/St."], result_df.loc[i,"Menge"], result_df.loc[i,"CO2 gesamt"] =\
                H.calc_co2(cf, user_value, entry[C.iS], nu_of_ppl)

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

            # get idx of question in result_df
            idx = result_df[result_df.Feld==advice.user_q.name].index.values

            # get advice content
            has_new_q = True if np.any(advice.suggested_q) else False
            has_new_v = True if np.any(advice.suggested_f) else False
            has_text = True if hasattr(advice, "text") else False

            # Calculate Reduction Effect
            old_co2 = result_df.loc[result_df["Feld"]==advice.user_q.name,"CO2 gesamt"].sum()
            new_q = advice.suggested_q if has_new_q else advice.user_q
            new_v = float(advice.suggested_f)*user_data[i,C.iV] if has_new_v else user_data[i,C.iV]
            new_co2 = 0
            for cf in new_q.calculationfactor_set.all():
                _,_,temp = H.calc_co2(cf,new_v,user_data[i,C.iS],nu_of_ppl)
                new_co2 += temp
            del temp
            reduction = new_co2-old_co2
            relative_reduction = reduction/result_df.loc[:,"CO2 gesamt"].sum()*100
            total_reduction += reduction

            # Create Advice string
            if len(advice.text)>0:
                advice_text = advice.text.format(
                    user_q=advice.user_q.name,
                    suggested_q=advice.suggested_q.name if has_new_q else None,
                    suggested_v=new_v if has_new_v else None,
                    reduction=reduction,relative_reduction=relative_reduction)
            else:
                # prepare advice text
                advice_text = ""

                # if different question suggested:
                if has_new_q:
                    advice_text +=  f"Ersetze '{advice.user_q.name}' mit '{advice.suggested_q.name}'. "

                # if different value suggested:
                if has_new_v:
                    if new_v < user_data[i,C.iV]:
                        direction = "Reduziere"
                    else:
                        direction = "Erhöhe"
                    advice_text +=  f"{direction} '{advice.user_q.name}' auf {new_v}. "

                # Result
                # advice_text +=  f"Resultat: {reduction:+.3f} kg ({relative_reduction:+.2f} %). "

            # save to result_df
            reduction_df.loc[c,"Option"] = advice_text
            reduction_df.loc[c,"Abs. Reduktion [kg]"] = reduction
            reduction_df.loc[c,"Rel. Gesamt-Reduktion [%]"] = round(relative_reduction*100)/100
            reduction_df.loc[c,"Feld"] = advice.user_q.name
            reduction_df.loc[c,"Produkt-Nr."] = str(idx)
            c+=1

    # total relative reduction
    total_relative_reduction = total_reduction/result_df.loc[:,"CO2 gesamt"].sum()*100
    if np.any(reduction_df):
        reduction_df.sort_values("Abs. Reduktion [kg]", inplace=True)

    ## Create output table
    # df with CO2 sum per question ("Feld"), sorted in descending order by CO2 gesamt:
    # table = H.sum_per(result_df, "Feld", reset_index=False, sort=True)

    # df with CO2 per Emission, sorted in descending order by CO2 gesamt:
    table = result_df.sort_values(["Kategorie","CO2 gesamt"], ascending=False)

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
        'co2_sum' : result_df.loc[:,"CO2 gesamt"].sum().round(2),
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
    if (request.method == "POST") & (request.POST.get('reset')=='Reset'):
        reset = True

    ## First Call
    if (request.method == "GET") or reset:
        print("first call")

        ## Initialize values
        nu_of_ppl = request.session["nu_of_ppl"]

        # get default number of ppl
        ppl_q = Question.objects.filter(name='Teilnehmende')[0]
        ppl_id = Question.objects.filter(name='Teilnehmende')[0].pk
        try:
            def_nu_of_ppl = float(DefaultAmount.objects.filter(question=ppl_q,template=event_template)[0].value)
        except:
            def_nu_of_ppl = 1


        # get question, default value, category and more
        if event_template.name=="Alle":
            data = np.zeros((len(Question.objects.all())-1, C.columns))
            i = 0
            for question in Question.objects.all():
                if question.name=="Teilnehmende":
                    pass
                else:
                    data[i,C.iQ] = question.pk
                    data[i,C.iC] = question.category.pk
                    data[i,C.iS] = True
                    data[i,C.iU] = False if question.unit in ["", " "] else True
                    data[i,C.iI] = False if question.info_text in ["", " "] else True
                    data[i,C.iO] = i
                    data[i,C.iV] = 0
                    i += 1
            del i
        else:
            def_amnts = event_template.defaultamount_set.all()
            if ppl_id in def_amnts.values_list("question",flat=True):
                data = np.zeros((len(def_amnts)-1, C.columns))
            else:
                data = np.zeros((len(def_amnts), C.columns))
            i = 0
            for df in def_amnts:
                if df.question.name=="Teilnehmende":
                    pass
                else:
                    data[i,C.iQ] = df.question.pk
                    data[i,C.iV] = float(df.value)
                    data[i,C.iC] = df.question.category.pk
                    data[i,C.iS] = df.scale
                    data[i,C.iU] = False if df.question.unit in ["", " "] else True
                    data[i,C.iI] = False if df.question.info_text in ["", " "] else True
                    data[i,C.iO] = i
                    i += 1
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

        ## Read session
        data = np.array(request.session['user_data'])

        ## Read user input

        nu_of_ppl = request.POST.get("TNs")

        # Read entered values
        for j,q in enumerate(data[:,C.iQ]):
            ui = request.POST.get(str(int(q)))
            data[j,C.iS] = 1 if request.POST.get("scale"+str(int(q)))=="on" else 0

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
                row[C.iS] = df.scale
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
            data = np.delete(data, obj=np.argwhere(data[:,C.iQ]==float(request.POST.get('remove_field'))),axis=0)

            # Update first and last bools
            data = H.get_first_and_last(data)


        ## Process User input

        # User pressed enter key
        if request.POST.get("enter"):
            print("enter")

            # save entered values
            request.session['user_data'] = data.tolist()
            request.session['nu_of_ppl'] = nu_of_ppl

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
            request.session['nu_of_ppl'] = nu_of_ppl

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
    request.session['nu_of_ppl'] = nu_of_ppl

    ## DEbug
    print("data:")
    print(data)


    ## Create context

    # Get model objects from IDs in numpy array
    q_list = []
    for qid in data[:,C.iQ]:
        q_list.append(get_object_or_404(Question, pk=int(qid)))

    misscats_list = []
    for mcid in missing_cats:
        misscats_list.append(get_object_or_404(Category, pk=mcid))

    missqs_list = []
    for mqid in missing_qs:
        missqs_list.append(get_object_or_404(Question, pk=mqid))

    # create context dict
    scale = ["checked" if d else "" for d in data[:,C.iS]]
    context = {
        'template_instance':event_template,
        'q_v_f_l_u_i_and_s':zip(q_list,data[:,C.iV],data[:,C.iF],data[:,C.iL],data[:,C.iU],data[:,C.iI],scale),
        'missing_qs':missqs_list,
        'missing_cats': misscats_list,
        'cat_added':added_cat,
        'new_c_q_list':new_c_q_list,
        'page_name':f"CO2 bei {event_template.name}",
        'page_header':f"Veranstaltung: {event_template.name}",
        'page_description':'Bitte trage die Menge der verschiedenen Posten ein:',
        'button_link':'/rechner',
        'TNs':nu_of_ppl,
    }

    # Render Form
    return render(request, 'rechner/fill_eventtemplate.html', context)

# show source
def source(request, source_id):
    s = get_object_or_404(Source,pk=source_id)
    context = {"source":s}
    return render(request, 'rechner/source.html',context)
