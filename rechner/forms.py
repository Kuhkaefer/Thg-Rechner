from django import forms
from rechner.models import EventTemplate, Question
from django.shortcuts import get_object_or_404  

class FillEvent(forms.Form):
    question_instance = get_object_or_404(Question, pk=1)
    fields = (forms.models.fields_for_model(question_instance)) # get field, not the content of it
    question_field = fields['question_text']
    print(question_field)
    #entry_field = question_instance.__meta.get_field('question_text').formfield()
    
