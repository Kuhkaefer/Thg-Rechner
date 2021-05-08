import numpy as np
from rechner import constants as C
from .models import EventTemplate, Question, DefaultAmounts, Category



# Get booleans for first and last question of category
def get_first_and_last(data):
    
    # TODO: Check whether data already sorted by category
    
    _, i_first_unique= np.unique(data[:,C.iC], return_index=True)
    i_last_unique = np.append(i_first_unique[1:]-1, [len(data[:,C.iC])-1])
        
    data[:,[C.iF,C.iL]]        = 0
    data[i_first_unique,C.iF]  = 1
    data[i_last_unique,C.iL]   = 1
    
    return data
    
# Get list of questions and categories, that are not in the form yet
def get_missing(data):
    
    # get missing questions
    all_qs= set(Question.objects.all().values_list('pk',flat=True))
    missing_qs= list(all_qs.difference(set(data[:,C.iQ])))
    
    # get missing categories
    all_cats     = set(Category.objects.all().values_list('pk',flat=True))
    missing_cats = list(all_cats.difference(set(data[:,C.iC])))
    
    return missing_qs, missing_cats
