from django.shortcuts import render, get_object_or_404, get_list_or_404  
from django.http import HttpResponse


def home(request):
    context = {
        'page_name':'Klimarina',
        'page_header':'Klimarina - CO2 Rechner für die jDPG',
        'page_description':'Berechne die CO2-Emissionen, die für deine jDPG-Veranstaltung anfallen:',
        'button_link':'rechner',
        'button_text':'Zum Rechner'
        }
    
    return render(request, 'rechner/simple_page.html', context)


def info(request):
    
    content = "Klimarina ist ein Projekt des Arbeitsteams 'Nachhaltigkeit' der jungen Deutschen Physikalischen Gesellschaft (jDPG)"
    
    context = {
        'page_name':'Klimarina - Info',
        'page_header':'Info',
        'page_description':'Über das Projekt, über uns und überhaupt',
        'page_content':content,
        }
    
    return render(request, 'rechner/simple_page.html', context)
