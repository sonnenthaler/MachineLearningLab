# -*- coding: utf-8 -*-
'''
Course: Machine Learning Lab given by Prof. Brefeld
Project: Influence of psychological factors of drug consumption
Authors: Johanna Regenthal and Sofija Engelson
Due date: 
'''

#-----------------------0.Preliminaries-----------------------------------------

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chisquare

#----------------------1.Reading and cleaning data-------------------------------

#----------------------1.1 Reading--------------------------------------------------
colnames = ['ID','Age','Gender','Education','Country','Ethnicity','Nscore','Escore','Oscore','Ascore','Cscore','Impulsiv','SS','Alcohol','Amphet','Amyl','Benzos','Caff','Cannabis','Choc','Coke','Crack','Ecstasy','Heroin','Ketamine','Legalh','LSD','Meth','Mushrooms','Nicotine','Semer','VSA']

PsychDrug = pd.read_csv('drug_consumption.data', names = colnames, header = None)
PsychDrug.head()

#----------------------1.2 Cleaning---------------------------------------------------

#----------1.2.1 Classification into Users and Non-users for all drugs------------------
# Imported from https://github.com/deepak525/Drug-Consumption/blob/master/drug.ipynb

DrugUse = ['Alcohol','Amphet', 'Amyl', 'Benzos', 'Caff', 'Cannabis', 'Choc', 'Coke', 'Crack',
           'Ecstasy', 'Heroin', 'Ketamine', 'Legalh', 'LSD', 'Meth', 'Mushrooms','Nicotine', 'Semer', 'VSA']
ClassificationDrugUse = ['User_Alcohol','User_Amphet', 'User_Amyl', 'User_Benzos', 'User_Caff', 'User_Cannabis', 'User_Choc', 'User_Coke', 'User_Crack',
           'User_Ecstasy', 'User_Heroin', 'User_Ketamine', 'User_Legalh', 'User_LSD', 'User_Meth', 'User_Mushrooms','User_Nicotine', 'User_Semer', 'User_VSA']

for column in DrugUse:
    le = LabelEncoder()
    PsychDrug[column] = le.fit_transform(PsychDrug[column])

for i in range(len(DrugUse)):
    PsychDrug.loc[((PsychDrug[DrugUse[i]]==0) | (PsychDrug[DrugUse[i]]==1)), ClassificationDrugUse [i]] = 'Non-user'
    PsychDrug.loc[((PsychDrug[DrugUse[i]]==2) | (PsychDrug[DrugUse[i]]==3) | (PsychDrug[DrugUse[i]]==4) | (PsychDrug[DrugUse[i]]==5) | (PsychDrug[DrugUse[i]]==6)), ClassificationDrugUse [i]] = 'User'

# PsychDrug.drop(columns = DrugUse)

#------------------1.2.2 Dequantification of explanatory variables------------------------

# Building dictionary which has the columns as key and the mapping of quantified number and 
# translation saved as a tuple in value
MappingDict = {}

MappingDict['Age'] = (-0.95197,'18-24'),\
    (-0.07854,'25-34'),\
    (0.49788,'35-44'),\
    (1.09449,'45-54'),\
    (1.82213,'55-64'),\
    (2.59171,'65+')
    
MappingDict['Gender'] = (0.48246,'Female'),(-0.48246,'Male')

MappingDict['Education'] =(-2.43591,'Left School Before 16 years'),\
    (-1.73790,'Left School at 16 years'),\
    (-1.43719,'Left School at 17 years'),\
    (-1.22751,'Left School at 18 years'),\
    (-0.61113,'Some College,No Certificate Or Degree'),\
    (-0.05921,'Professional Certificate/ Diploma'),\
    (0.45468,'University Degree'),\
    (1.16365,'Masters Degree'),\
    (1.98437,'Doctorate Degree')

MappingDict['Country'] =(-0.09765,'Australia'),\
    (0.24923,'Canada'),\
    (-0.46841,'New Zealand'),\
    (-0.28519,'Other'),\
    (0.21128,'Republic of Ireland'),\
    (0.96082,'UK'),\
    (-0.57009,'USA')

MappingDict['Ethnicity'] = (-0.50212,'Asian'),\
    (-1.10702,'Black'),\
    (1.90725,'Mixed-Black/Asian'),\
    (0.12600,'Mixed-White/Asian'),\
    (-0.22166,'Mixed-White/Black'),\
    (0.11440,'Other'),\
    (-0.31685,'White')
    
# MappingDict is missing for the following columns: Nscore','Escore','Oscore','Ascore','Cscore'

# Rounding all floats to 5 places after comma for further replacement
PsychDrug = round(PsychDrug,5)

# Function to replace the 
def mapping(data, col):
    rep = data[col]
    for value in MappingDict[col]:
        rep = rep.replace(value[0], value[1])
    return rep

PsychDrug['Age'] = mapping(PsychDrug,'Age')
PsychDrug['Gender'] = mapping(PsychDrug,'Gender')
PsychDrug['Education'] = mapping(PsychDrug,'Education')
PsychDrug['Country'] = mapping(PsychDrug,'Country')
PsychDrug['Ethnicity'] = mapping(PsychDrug,'Ethnicity')

#---------------------2. Exploratory analysis------------------------------------
# Imported from https://github.com/deepak525/Drug-Consumption/blob/master/drug.ipynb

# Visualization of frequency of usage for each drug
fig, axes = plt.subplots(5,3,figsize = (16,16))
fig.suptitle("Count of Different Classes Vs Drug",fontsize=14)
k=0
for i in range(5):
    for j in range(3):
        sns.countplot(x=DrugUse[k], data=PsychDrug,ax=axes[i][j])
        k+=1

plt.tight_layout()
plt.show()

# Visualization of Users vs. Non-users for each drug
count_of_users = []
count_of_non_users = []

for i in range(len(DrugUse)):
    s = PsychDrug.groupby([ClassificationDrugUse[i]])[DrugUse[i]].count()
    count_of_users.append(s[1])
    count_of_non_users.append(s[0])

bins = np.arange(1,20,1)
plt.figure(figsize=(16,6))
plt.bar(bins+0,count_of_users,width=0.4,label ='User')
plt.bar(bins+.30,count_of_non_users,width=0.4,label ='Non-User')
plt.xticks(bins,DrugUse,rotation=50,fontsize=13)
plt.ylabel("Count",fontsize=13)
plt.title("Drug Vs User Or Non-user",fontsize=15)
plt.legend()

#--------------------------Testing--------------------------------------------

data_crosstab = pd.crosstab(PsychDrug['Age'],  
                            PsychDrug['Education'], 
                                margins = False)
chisquare(data_crosstab)

ExpVar = ['Age','Gender','Education','Country','Ethnicity']
PsychVar = ['Nscore','Escore','Oscore','Ascore','Cscore']

X = PsychDrug[ExpVar]
cov_X = np.cov(X)
plot_values = np.vstack(cov_X)
fig1 = plt.figure()
plt.title('Covariance Matrix Representation (in log)')
ax1 = fig1.add_subplot(111)
cax1 = ax1.matshow(plot_values, interpolation='nearest')
fig1.colorbar(cax1)


cor_X = np.corrcoef(PsychDrug[PsychVar])
fig = plt.figure()
plt.title('Correlation Matrix Representation')
ax = fig.add_subplot(111)
cax = ax.matshow(np.corrcoef(cor_X), interpolation='nearest')
fig.colorbar(cax)