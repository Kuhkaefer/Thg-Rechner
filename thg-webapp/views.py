from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from rechner.models import Stats


def home(request):

    # count landing
    calculations = get_object_or_404(Stats,name="home_landing")
    calculations.count += 1
    calculations.save()

    context = {
        'page_name':'Klimarina',
        'page_header':'Klimarina: Der CO<sub>2</sub>-Rechner für die jDPG',
        'page_description':'Berechne die CO2-Emissionen, die für deine jDPG-Veranstaltung anfallen:',
        'button_link':'rechner',
        'button_text':'Zum Rechner'
        }

    return render(request, 'rechner/simple_page.html', context)


def info(request):

    # count landing
    calculations = get_object_or_404(Stats,name="info_landing")
    calculations.count += 1
    calculations.save()

    content = 'Klimarina ist ein Projekt des Arbeitsteams Nachhaltigkeit der jungen Deutschen \
                Physikalischen Gesellschaft (jDPG).<br>Mit unserem Treibhausgasrechner möchten wir eine \
                einfache Abschätzung der Treibhausgasemissionen und Einsparpotentialen bei \
                jDPG-Veranstaltungen ermöglichen.\
                Wenn du Fragen hast oder Interesse, an dem Projekt mitzuwirken, melde dich gerne \
                beim <a href = "https://www.dpg-physik.de/vereinigungen/fachuebergreifend/ak/akjdpg/\
                wir/arbeitsteams/nachhaltigkeit/nachhaltigkeit">Arbeitsteam Nachhaltigkeit</a>.\
                <br><br>Anmerkung: Alle Treibhausgaswerte werden übrigens in CO<sub>2</sub>-Äquivalenten angegeben \
                (CO<sub>2eq</sub>), auch wenn die Bezeichnung "CO<sub>2</sub>" verwendet wird.\
                 Andere Treibhausgase wie beispielsweise Methan sind in \
                Äquivalenten von CO<sub>2eq</sub> mit einkalkuliert.\
                <br><br>Letztes Update: November 2022'

    context = {
        'page_name':'Klimarina - Info',
        'page_header':'Info',
        'page_description':'Über das Projekt, über uns und überhaupt:',
        'page_content':content,
        }

    return render(request, 'rechner/simple_page.html', context)
