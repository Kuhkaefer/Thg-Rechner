from django.shortcuts import render, get_object_or_404, get_list_or_404  
from django.http import HttpResponse


def home(request):
    context = {
        'page_name':'Klimarina',
        'page_header':'Home',
        'page_description':'Look around. Nice and homely here. Soothing. Welcome.',
        'button_link':'rechner',
        'button_text':'Zum Rechner'
        }
    
    return render(request, 'rechner/simple_page.html', context)
