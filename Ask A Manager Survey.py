# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 16:09:22 2022

@author: billp
"""

import pandas as pd
import seaborn as sns
import re

amsurvey = pd.read_csv("C:/Users/billp/Downloads/askamanagersurvey.csv")

#rename some columns for easier use
amsurvey.rename(columns = {"Timestamp": "timestamp", "How old are you?": "age", "What industry do you work in?": "industry", 
                           "Job title": "job_title", "If your job title needs additional context, please clarify here:":
                           "job_comments", "What is your annual salary? (You'll indicate the currency in a later question. If you are part-time or hourly, please enter an annualized equivalent -- what you would earn if you worked the job 40 hours a week, 52 weeks a year.)":
                           "salary", "How much additional monetary compensation do you get, if any (for example, bonuses or overtime in an average year)? Please only include monetary compensation here, not the value of benefits.":
                           "add_bonus", "Please indicate the currency": "currency",
                           'If "Other," please indicate the currency here: ': "currency_other", 
                           "If your income needs additional context, please provide it here:": "income_comments",
                           "What country do you work in?": "country", "If you're in the U.S., what state do you work in?": "us_state",
                           "What city do you work in?": "city", "How many years of professional work experience do you have overall?": "total_experience",
                           "How many years of professional work experience do you have in your field?": "sector_experience",
                           "What is your highest level of education completed?": "highest_education",
                           "What is your gender?": "gender", "What is your race? (Choose all that apply.)": "race"}, inplace = True)

#print (amsurvey.columns)

#quick exploring of the various columns to check structure and errors
def explore (name):
    
    name = str(amsurvey.columns[name])
    
    print (amsurvey[name].head(5))
    print ("Missing percentage:", amsurvey[name].isnull().sum()/len(amsurvey))
    
    if type(amsurvey[name][0]) == str:
        
        print (amsurvey[name].unique()); print (len(amsurvey[name].unique()))
        
    elif type(amsurvey[name][0]) != str:
        
        print (amsurvey[name].max()); print (amsurvey[name].min())
        print (amsurvey[name].mean()); print (amsurvey[name].var())
        
        sns.boxplot(x = amsurvey[name])
        
#explore (17)

#fix of column 6, holding the salaries
amsurvey.salary = amsurvey.apply(lambda x: int(x.salary.replace(",", "")) if "," in x.salary else int(x.salary), axis = 1)

#inspecting the different currencies
#print (amsurvey.currency.value_counts()["Other"])

"""seeing how there's only 154 entries with an 'other' currency type, they will be removed as the salary is one of the most
important variables of this algorithm"""

amsurvey = amsurvey[amsurvey.currency != "Other"]

#salary and bonus conversion to euros
currency_exchange = {"currency": ['USD', 'GBP', 'CAD', 'EUR', 'AUD/NZD', 'CHF', 'ZAR', 'SEK', 'HKD', 'JPY'],
                     "value": [0.939189, 1.12919, 0.695526, 1, 0.633316, 1.01049, 0.0543444, 0.0898271, 0.120394, 0.00703646]}

currency_exchange = pd.DataFrame(currency_exchange)

amsurvey["euro_salary"] = None
amsurvey["euro_bonus"] = None

for i in range(len(currency_exchange)):
    amsurvey.loc[(amsurvey.currency == currency_exchange.currency.iloc[i]), ["euro_salary"]] = (amsurvey.salary * currency_exchange.value.iloc[i])
    amsurvey.loc[(amsurvey.currency == currency_exchange.currency.iloc[i]), ["euro_bonus"]] = (amsurvey.add_bonus * currency_exchange.value.iloc[i])

#fix of column 11 with the country names

"""Do note that this is a situational script aimed at narrowing down and correcting the most common errors, 
NOT code to identify and account for all the cases. Given enough time I could develop such a piece of code, 
but this is not the purpose of this excersise."""

def country_corr (cc):
    
    if re.search(r"^(U|u)(|.+)(S|s)(|.+)", cc) != None or re.search(r"(?:(A|a)(M|m)(E|e)(R|r))", cc) != None or cc in [
            " US", "🇺🇸 "] or re.search(r".+(S|s)tate.+", cc) != None:
        cc = "United States of America" 
    elif re.search(r"^(U|u)(|.+)(K|k)(|.+)", cc) != None or re.search(r"(E|e)(N|n)(G|g)(L|l)", cc) != None or re.search(
            r"(B|b)(R|r)(I|i)(T|t)", cc) != None or re.search(r"(nited) (ingdom)", cc) != None:
        cc = "United Kindgom"
    elif re.search(r"(?:(C|c)(A|a)(N|n)(A|a))", cc) != None:
        cc = "Canada"
    elif re.search(r"(|.+)(Z|z)(ealand)(|.+)", cc) != None:
        cc = "New Zealand"
    elif re.search(r".+(etherland).+", cc) != None:
        cc = "The Netherlands"
    elif re.search(r".+(ustrali).+", cc) != None:
        cc = "Australia"
    elif re.search(r".+(ermany).+", cc) != None:
        cc = "Germany"
    elif re.search(r".+(reland).+", cc) != None:
        cc = "Ireland"
    return (cc)

amsurvey.country = amsurvey.apply(lambda x: country_corr(x.country), axis = 1)
#print (amsurvey.groupby("country").size())

amsurvey = amsurvey[amsurvey["country"].groupby(amsurvey["country"]).transform("size") > 9]
#print (amsurvey.groupby("country").size())
#print (len(amsurvey))

"""These preceding lines of code narrow correct and narrow down the entries for countries. The 'country_corr' function 
specifically corrects some common errors regarding the erroneous entries in the 'country' column. The top part of the 
function is mostly flex; however the entire function showcases my comfort at using regular expressions. It is of course
certain that with 28 thousand entries, some will be erroneously sorted on the aftermath of this function. Following that,
I am removing the groups that are underrepresented in the dataset, as any analysis regarding those would be inconclusive
and it would hamper the effectiveness of the models to follow. """

"""Now that I have a decent grasp on my data and the kind of research that I will be performing, I am removing
the columns that will not be of particular use, namely the 'comments' columns and the one containing different 
currencies. The entries are very few and difficult to analyze."""

amsurvey = amsurvey[["age", "industry", "job_title", "salary", "add_bonus", "currency", "country", "us_state", 
                    "city", "total_experience", "sector_experience", "highest_education", "gender", "race", "euro_salary", 
                    "euro_bonus"]]
#print (amsurvey.columns)

###EXPLORE THE DATA

"""Now that we have had a brief look into the nature of the data and we have tidied it up into a more manageable form, it is 
time to take a look into the variables and their distributions."""

#print (amsurvey.groupby("race").size()); sns.countplot(data = amsurvey, x = "race")
amsurvey = amsurvey[["age", "industry", "job_title", "salary", "add_bonus", "currency", "country", "us_state", 
                    "city", "total_experience", "sector_experience", "highest_education", "gender", "euro_salary", 
                    "euro_bonus"]]

"""apparently the vast majority of the participants were of "White" race, which renders any analysis on it inconclusive. 
furthermore, seeing how the participants come from all over the world, a correlation between race and salary would be 
expected"""

#print (amsurvey.groupby("gender").size())

"""the 'other or prefer not to answer' option is a little misleading; however this is the data we're dealing with.
i shall rename the lone 'prefer not to answer' entry to be included along the rest. interestingly, the survey includes
a lot more women than men."""

amsurvey.gender.loc[(amsurvey.gender == "Prefer not to answer")] = "Other or prefer not to answer"
#sns.countplot(data = amsurvey, y = "gender")

#sns.countplot(data = amsurvey, x = "country")

#sns.countplot(data = amsurvey[amsurvey["country"].groupby(amsurvey["country"]).transform("size") > 200], x = "country")

#sns.displot(data = amsurvey, kind = "hist", x = "euro_salary")
#sns.displot(data = amsurvey[amsurvey["euro_salary"] < 300000], kind = "hist", x = "euro_salary", bins = 30)

#sns.displot(data = amsurvey[amsurvey["euro_bonus"] < 40000], kind = "hist", x = "euro_bonus", bins = 20)

#sns.countplot(data = amsurvey, y = "total_experience")

#sns.countplot(data = amsurvey, y = "sector_experience")

#sns.countplot(data = amsurvey, y = "highest_education")

#sns.countplot(data = amsurvey, y = "country")
print (amsurvey.columns)