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
import ast

## Index Seite (Choose Eventtemplate)
def index(request):

    if request.method == "POST":

        # generate ID for Session
        if "id" in request.session.keys():
            request.session["id"] += 1
        else:
            request.session["id"] = 0
        session_id = str(request.session["id"])
        request.session[session_id] = {}

        # Check template choice and nu of ppl, If button clicked (I think)
        choice = request.POST.get('chosen_template')

        # no choice
        if choice == "":
            choice = "/rechner"

        # valid choice
        else:
            request.session[session_id]["template_id"] = choice

            # get number of participants
            if len(request.POST.get('nu_of_ppl')) > 0:
                nu_of_ppl = int(request.POST.get('nu_of_ppl'))
            else:
                event_template = get_object_or_404(EventTemplate, pk=choice)
                nu_of_ppl = event_template.participants

            request.session[session_id]['nu_of_ppl'] = nu_of_ppl
            return HttpResponseRedirect(f'event{session_id}')

    # If first call of page
    else:
        choice=""

    # create context
    context = {
        'page_name':'Klimarina',
        'page_header':'CO<sub>2</sub>-Rechner',
        'page_text':"Wähle ein Veranstaltungsformat als Vorlage:",
        'event_templates':EventTemplate.objects.all(),
        'button_link':'/rechner',
        'button_text':'Los!'
        }

    # render context into page
    return render(request,'rechner/choose_eventtemplate.html',context)

## Abfrage-Seite
def fill_event_template(request, session_id):

    ## Always 1
    template_id = request.session[session_id]["template_id"]

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
        nu_of_ppl = request.session[session_id]["nu_of_ppl"]
        event_name = event_template.name.replace("&","&#38;").replace(" ","&nbsp;")

        # get default number of ppl
        def_nu_of_ppl = event_template.participants

        # get question, default value, category and more
        # all questions
        if event_template.name=="Alle":
            data = np.zeros((len(Question.objects.all()), C.columns))
            c_names = []
            i = 0
            for question in Question.objects.all():
                data[i,C.iQ] = question.pk
                data[i,C.iC] = question.category.pk
                data[i,C.iS] = True
                data[i,C.iU] = False if question.unit in ["", " "] else True
                data[i,C.iI] = False if question.info_text in ["", " "] else True
                data[i,C.iO] = i
                data[i,C.iV] = 0
                c_names.append(question.category.name)
                i += 1
            del i
        # normal event template
        else:
            def_amnts = event_template.defaultamount_set.all()
            data = np.zeros((len(def_amnts), C.columns))
            c_names = []
            i = 0
            for df in def_amnts:
                data[i,C.iQ] = df.question.pk
                data[i,C.iV] = float(df.value)
                data[i,C.iC] = df.question.category.pk
                data[i,C.iS] = df.scale
                data[i,C.iU] = False if df.question.unit in ["", " "] else True
                data[i,C.iI] = False if df.question.info_text in ["", " "] else True
                data[i,C.iO] = i
                c_names.append(df.question.category.name)
                i += 1
            del i

        # sort by category and order

        idx = np.lexsort((data[:,C.iO],c_names))
        data = data[idx]

        # get first and last bools
        data = H.get_first_and_last(data)

        # Non relevant quantites
        added_cat = None
        new_c_q_list = None


    ## Later Call
    elif request.method == "POST":
        print("later call")

        ## Read session
        data = np.array(request.session[session_id]['user_data'])

        ## Read user input

        # read event name and number of participants
        event_name = request.POST.get("event_name").replace(" ","&nbsp;")
        if event_name=="":
            event_name = get_object_or_404(EventTemplate,pk=event_template.pk).name
        nu_of_ppl = int(float(request.POST.get("TNs")))
        if nu_of_ppl is None:
            nu_of_ppl = 1


        # Read entered values
        if len(data)>0:
            for j,q in enumerate(data[:,C.iQ]):

                # freshly added field & page reloaded
                if request.POST.get('new_field') != None:
                    added_field_qid = int(request.POST.get("new_field"))
                    if (q==added_field_qid):
                        data[j,C.iS] = 1
                        ui = data[j,C.iV]
                    else:
                        ui = request.POST.get(str(int(q)))
                        data[j,C.iS] = 1 if request.POST.get("scale"+str(int(q)))=="on" else 0
                # normally
                else:
                    ui = request.POST.get(str(int(q)))
                    data[j,C.iS] = 1 if request.POST.get("scale"+str(int(q)))=="on" else 0
                if np.isscalar(ui):
                    data[j,C.iV] = ui
                else:
                    try:
                        data[j,C.iV] = eval(ui)
                    except:
                        print(f"failed to eval {ui}")
                        data[j,C.iV] = None
                        can_submit=False
            del j

        # Read added fields
        refresh_add = False
        added_field_qid = None
        if request.POST.get('new_field') != None:
            print("field added")
            added_field_qid = int(request.POST.get("new_field"))

            # User did add field
            if added_field_qid >= 0:
                added_q = get_object_or_404(Question, pk=added_field_qid)
                if (len(data)>0):
                    if (added_q.pk not in data[:,C.iQ]):
                        row = np.zeros(data[0].shape)
                        row[C.iQ] = added_field_qid
                        row[C.iC] = added_q.category.pk
                        row[C.iS] = 1
                        row[C.iV] = 0
                        row[C.iO] = np.max(data[:,C.iO])+1
                        row[C.iU] = False if added_q.unit in ["", " "] else True
                        row[C.iI] = False if added_q.info_text in ["", " "] else True

                        # insert into data array
                        if row[C.iC] in data[:,C.iC]:
                            idx = np.max(np.where(data[:,C.iC]==row[C.iC]))
                        else:
                            # cnames=list(Categories.objects.filter(pk__in=np.unique(data[:,C.iC])).values_list("name",flat=True))
                            idx = len(data)-1

                        data=np.insert(data.T,idx+1,row,axis=1).T

                        # Update first and last bools
                        data = H.get_first_and_last(data)

                    # page was refreshed after adding a new question
                    else:
                        refresh_add = True

                # if data was empty
                else:
                    data = np.zeros((1,C.columns))
                    data[0,C.iQ] = added_field_qid
                    data[0,C.iC] = added_q.category.pk
                    data[0,C.iS] = 1
                    data[0,C.iO] = 0
                    data[0,C.iV] = 0
                    data[0,C.iF] = 1
                    data[0,C.iL] = 1
                    data[0,C.iU] = False if added_q.unit in ["", " "] else True
                    data[0,C.iI] = False if added_q.info_text in ["", " "] else True

        # Read added Category
        if request.POST.get('new_cat')!=None:
            print("category added")
            added_cat_id = int(request.POST.get("new_cat"))
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
            print("field removed")
            data = np.delete(data, obj=np.argwhere(data[:,C.iQ]==float(request.POST.get('remove_field'))),axis=0)

            # Update first and last bools
            data = H.get_first_and_last(data)


        ## Process User input

        # User pressed enter key or pressed submit button
        if request.POST.get("enter") or request.POST.get("submit form"):
            print("submit")

            # save entered values
            request.session[session_id]['user_data'] = data.tolist()
            request.session[session_id]['nu_of_ppl'] = nu_of_ppl
            request.session[session_id]['event_name'] = event_name

            if can_submit:
                # Move on to next page
                return HttpResponseRedirect(f'/rechner/result{session_id}')
            else:
                pass


    ## Always

    # get missing qs and cats
    missing_qs, missing_cats = H.get_missing(data)

    ## Save data
    request.session[session_id]['event_template_id'] = template_id
    request.session[session_id]['user_data'] = data.tolist()
    request.session[session_id]['nu_of_ppl'] = nu_of_ppl
    request.session[session_id]['event_name'] = event_name

    ## Create context

    # Get model objects from IDs in numpy array
    q_list = []
    if len(data)>0:
        for qid in data[:,C.iQ]:
            q_list.append(get_object_or_404(Question, pk=int(qid)))

    misscats_list = []
    for mcid in missing_cats:
        misscats_list.append(get_object_or_404(Category, pk=mcid))

    missqs_list = []
    for mqid in missing_qs:
        missqs_list.append(get_object_or_404(Question, pk=mqid))

    # create context dict
    if len(data)>0:
        scale = ["checked" if d else "" for d in data[:,C.iS]]
        q_v_f_l_u_i_and_s = zip(q_list,data[:,C.iV],data[:,C.iF],data[:,C.iL],data[:,C.iU],data[:,C.iI],scale)
    else:
        scale = []
        q_v_f_l_u_i_and_s = None
    context = {
        'template_instance':event_template,
        'q_v_f_l_u_i_and_s':q_v_f_l_u_i_and_s,
        'missing_qs':missqs_list,
        'missing_cats': misscats_list,
        'cat_added':added_cat,
        'new_c_q_list':new_c_q_list,
        'page_name':f"CO2 bei {event_template.name}",
        'page_header':f"Veranstaltung: {event_template.name}",
        'page_description':'',
        'button_link':'/rechner',
        'TNs':nu_of_ppl,
        'event_name':event_name,
    }

    # Render Form
    return render(request, 'rechner/fill_eventtemplate.html', context)

## Ergebnis Seite
def result(request, session_id):

    # Chosen Event-Template
    event_template = request.session[session_id]['event_template_id']

    # event name
    event_name = request.session[session_id]["event_name"]

    # Array with users answers to questions of event template
    user_data = np.array(request.session[session_id]["user_data"])
    nu_of_ppl = int(float(request.session[session_id]["nu_of_ppl"]))

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
            result_df.loc[i,"Quelle"] = str(list(emi.source.all().values_list("pk",flat=True)))

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
            has_new_q = False if advice.suggested_q is None else True
            has_new_v = False if advice.suggested_f is None else True
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
                    advice_text +=  f'Ersetze "{advice.user_q.name}" mit "{advice.suggested_q.name}". '

                # if different value suggested:
                if has_new_v:
                    if new_v < user_data[i,C.iV]:
                        direction = "Reduziere"
                    else:
                        direction = "Erhöhe"
                    if has_new_q:
                        if advice.suggested_q.unit != advice.user_q.unit:
                            direction = "Ändere"
                            unit = advice.suggested_q.unit
                            if user_data[i,C.iS]:
                                unit += " pro TN"
                            suggestion = new_v
                        else:
                            unit = "%"
                            suggestion = 100*advice.suggested_f
                        advice_text +=  f'{direction} "{advice.suggested_q.name}" auf {suggestion:.0f} {unit}. '
                    else:
                        advice_text +=  f'{direction} "{advice.user_q.name}" auf {advice.suggested_f*100:.0f} %. '

                # Result
                # advice_text +=  f"Resultat: {reduction:+.3f} kg ({relative_reduction:+.2f} %). "
            # save to result_df
            reduction_df.loc[c,"Option"] = advice_text
            reduction_df.loc[c,"Abs. Reduktion [kg]"] = reduction
            reduction_df.loc[c,"Rel. Reduktion [%]"] = round(relative_reduction*100)/100
            reduction_df.loc[c,"Feld"] = advice.user_q.name
            reduction_df.loc[c,"Produkt-Nr."] = str(idx)
            reduction_df.loc[c,"Hinweis"] = advice.info
            c+=1

    # filter out minor reductions
    # large_red = reduction_df["Abs. Reduktion [kg]"] < 0.05*reduction_df["Abs. Reduktion [kg]"].min()
    # reduction_df = reduction_df[large_red.values].reset_index(drop=True)

    # total relative reduction
    if np.any(reduction_df):
        reduction_df.sort_values("Abs. Reduktion [kg]", inplace=True)
        total_reduction = reduction_df.groupby("Feld").first().loc[:,"Abs. Reduktion [kg]"].sum()
        total_relative_reduction = total_reduction/result_df.loc[:,"CO2 gesamt"].sum()*100
    else:
        total_reduction = 0
        total_relative_reduction = 0

    ### Plot result

    ## pie chart
    fig = go.Figure(px.pie(H.sum_per(result_df, "Kategorie"), names="Kategorie",
                    values="CO2 gesamt", color="Kategorie", width=500, height=300,
                    color_discrete_map=C.colors))

    fig.update_layout(legend = {'title_text':'Kategorie','x' : 1.1, 'y':0.6, 'yanchor':'middle'},
                      margin=go.layout.Margin(
                        l=20, #left margin
                        r=20, #right margin
                        b=0, #bottom margin
                        t=0, #top margin
                      ),
                      yaxis={'ticksuffix':"kg"}
                      )
    fig.update_traces(hovertemplate="%{label}<br>%{value} kg")
    pie_chart = plot(fig,output_type='div',config={'displayModeBar':False})

    ## horizontal bars

    # Create emission table
    # df with CO2 sum per question ("Feld"), sorted in descending order by CO2 gesamt:
    # table = H.sum_per(result_df, "Feld", reset_index=False, sort=True)

    # df with CO2 per Emission, sorted in descending order by CO2 gesamt:
    em_table = result_df.sort_values(["CO2 gesamt"], ascending=False)

    # filter out minor emissions
    large_ems = em_table["CO2 gesamt"] > 0.01*em_table["CO2 gesamt"].max()
    remainder = em_table.loc[~large_ems.values,"CO2 gesamt"].sum()
    remainding_ems = ", ".join(em_table.loc[~large_ems.values,"Produkt"].tolist())
    em_table = em_table[large_ems.values].reset_index(drop=True)

    # Create emission names
    for i,row in em_table.iterrows():
        tn = " pro TN" if row["·TN"] else ""
        source = ast.literal_eval(row['Quelle'])
        if len(source)==0:
            source=""
        else:
            source = [f'<a href="/rechner/source/{s}">{s}</a>' for s in source]
            source = f"[{', '.join(source)}]"
        em_table.loc[i,"fullname"] = \
        f' <b>{row["Produkt"]}</b> ({round(row["Menge"]*100)/100}{row["Einheit"]} {tn}) {source}'

    # Add remainder
    em_table = em_table.append(pd.DataFrame({
                                "CO2 gesamt":[remainder],
                                "fullname":[" …Rest…"],
                                "Kategorie":'Rest',
                                "Feld":"…"}),ignore_index=True)
    em_table["CO2 gesamt"] = em_table["CO2 gesamt"].round(2)


    # create figure
    fig = go.Figure(px.bar(em_table,x="CO2 gesamt",y="fullname", orientation="h",
                           width=560, height=20*em_table.shape[0]+75,color="Kategorie",
                           labels={"CO2 gesamt":"CO<sub>2</sub> [kg]","fullname":""},
                           color_discrete_map=C.colors,custom_data=em_table,
                           # category_orders={'index': em_table.index.astype(str)}
                           ))
    fig.update_layout(yaxis={'title_font_size':1, 'side':'right',
                             'categoryorder':'total ascending',
                             # 'categoryarray':em_table.index
                             },
                      xaxis={"showgrid":True,"gridcolor":"grey","autorange" : "reversed"},
                      margin=go.layout.Margin(
                        l=20, #left margin
                        r=20, #right margin
                        b=40, #bottom margin
                        t=30, #top margin
                      ),
                      plot_bgcolor='rgba(0,0,0,0)')
    fig.update_traces(showlegend=False,
                      hovertemplate="Aus: %{customdata[1]}<br>%{value} kg")
    bar_chart = plot(fig, output_type='div',config={'displayModeBar':False})

    # Create output
    context = {
        'page_name':'CO2 Resultat',
        'page_header':f'Ergebnis für "{event_name}"',
        'page_description': f'',
        'reduction_table' : reduction_df.to_html(),
        'op_red' : zip(reduction_df.Option,
                       reduction_df["Rel. Reduktion [%]"].round(3),
                       reduction_df["Abs. Reduktion [kg]"].round(3)),
        'loops' : len(reduction_df),
        'co2_sum' : result_df.loc[:,"CO2 gesamt"].sum().round(2),
        'pie':pie_chart,
        'bars':bar_chart,
        'total_relative_reduction':round(total_relative_reduction*100)/100,
        }

    return render(request, 'rechner/result.html', context)


# show source
def source(request, source_id):
    s = get_object_or_404(Source,pk=source_id)
    context = {"source":s}
    return render(request, 'rechner/source.html',context)
