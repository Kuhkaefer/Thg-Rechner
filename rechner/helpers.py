import numpy as np
import pandas as pd
from rechner import constants as C
from .models import EventTemplate, Question, DefaultAmount, Category, CalculationFactor


# Get booleans for first and last question of category
def get_first_and_last(data):

    # TODO: Check whether data already sorted by category

    if len(data)>0:
        _, i_first_unique= np.unique(data[:,C.iC], return_index=True)
        
        i_last_unique = i_first_unique-1
        i_last_unique = i_last_unique[i_last_unique>=0]
        i_last_unique = np.append(i_last_unique,len(data[:,C.iC])-1)

        data[:,[C.iF,C.iL]]        = 0
        data[i_first_unique,C.iF]  = 1
        data[i_last_unique,C.iL]   = 1

    return data

# Get list of questions and categories, that are not in the form yet
def get_missing(data):

    # get all questions and categories
    all_qs= set(Question.objects.all().values_list('pk',flat=True))
    all_cats     = set(Category.objects.all().values_list('pk',flat=True))


    # get missing questions and categories (if data has rows)
    if len(data.shape)>1:
        missing_qs= list(all_qs.difference(set(data[:,C.iQ])))
        missing_cats = list(all_cats.difference(set(data[:,C.iC])))
    else:
        missing_qs = list(all_qs)
        missing_cats = list(all_cats)


    return missing_qs, missing_cats


# Calculate CO2 for single Question's Emission
def calc_co2(calc_factor, value, scale, nu_of_ppl):

        # get emission and question
        emi = calc_factor.emission
        question = calc_factor.question

        # Check units
        if question.unit != emi.unit:
            raise Exception(f"Unit Mismatch!: \"{question.name}\" expects {question.unit}, wheras \"{emi.name}\" requires {emi.unit}.")

        # get amount
        if calc_factor.fixed:
            if value==0:
                amount = 0
            else:
                amount = float(calc_factor.factor)
        else:
            amount = float(calc_factor.factor)*value

        # get emission per unit & consider emission factors
        co2_per_unit =  float(emi.value)
        for emission_factor in emi.factor.all():
            co2_per_unit *= float(emission_factor.value)


        # multiply with amount
        co2_sum = co2_per_unit  * amount

        # multiply with participants
        if scale:
            co2_sum *= nu_of_ppl

        # finalise
        return co2_per_unit, amount, co2_sum


# get CO2 sum per unique entry in column "col"
def sum_per(result_df, col, drop_zero=True, on_col="CO2 gesamt", reset_index=True, sort=False, sort_on=None):
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
