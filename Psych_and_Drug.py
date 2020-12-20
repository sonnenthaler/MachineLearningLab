# -*- coding: utf-8 -*-
'''
Course: Machine Learning Lab given by Prof. Brefeld
Project: Influence of psychological factors on drug consumption
Authors: Johanna Regenthal and Sofija Engelson
Due date: 
'''

#-----------------------0.Preliminaries-----------------------------------------
#%%
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency, norm, multinomial
from matplotlib import patches as mpatches
from pomegranate import *
from pomegranate.utils import plot_networkx
import networkx
from itertools import combinations, chain
from sklearn.preprocessing import KBinsDiscretizer
import math



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
    PsychDrug.loc[((PsychDrug[DrugUse[i]]==0) | (PsychDrug[DrugUse[i]]==1)), ClassificationDrugUse [i]] = False
    PsychDrug.loc[((PsychDrug[DrugUse[i]]==2) | (PsychDrug[DrugUse[i]]==3) | (PsychDrug[DrugUse[i]]==4) | (PsychDrug[DrugUse[i]]==5) | (PsychDrug[DrugUse[i]]==6)), ClassificationDrugUse [i]] = True

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
#%%
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
plt.show()

#----------------------------------------------------------------------------
# Visualization of the correlations and covariances between all continuous variables
# grouped by drug use frequencies and psychological variables

PsychVar = ['Nscore','Escore','Oscore','Ascore','Cscore','Impulsiv','SS']

corMatDrugUse = PsychDrug[DrugUse].corr()
corMatPsychVar = PsychDrug[PsychVar].corr()

covMatDrugUse = PsychDrug[DrugUse].cov()
covMatPsychVar = PsychDrug[PsychVar].cov()

ax = plt.axes()
sns.heatmap(corMatDrugUse, ax = ax)
ax.set_title('Correlation heatmap for drug use frequencies')
plt.show()

ax = plt.axes()
sns.heatmap(corMatPsychVar, ax = ax)
ax.set_title('Correlation heatmap for psychological factors')
plt.show()

ax = plt.axes()
sns.heatmap(covMatDrugUse, ax = ax)
ax.set_title('Covariance heatmap for drug use frequencies')
plt.show()

ax = plt.axes()
sns.heatmap(covMatPsychVar, ax = ax)
ax.set_title('Covariance heatmap for psychological factors')
plt.show()

# Chi-Square test for correlation between two categorial variables (demographic variable --> usage classification)
# For example: Education and usage of nicotine

def perform_chi_test(v1, v2):
    table = pd.crosstab(PsychDrug[v1], PsychDrug[v2], margins = False)
    stat, p, dof, expected = chi2_contingency(table)
    alpha = 0.05
    #print('significance=%.3f, p=%.3f' % (alpha, p))
    if p <= alpha:
        print(v1 + ' and ' + v2 + ' are dependent because H0 can be rejected with a p-value of p=%.3f.' % p)
    else:
        print(v1 + ' and ' + v2 + ' are independent because H0 can not be rejected with a p-value of p=%.3f.' % p)

perform_chi_test('Education', 'User_Nicotine')

# Definition of a cumulative variable which indicates users (dacade-based) of legal and illegal drugs
LegalDrugs = ['User_Alcohol', 'User_Caff', 'User_Choc', 'User_Coke', 'User_Nicotine']
IllegalDrugs = ['User_Amphet', 'User_Amyl', 'User_Benzos','User_Cannabis', 'User_Crack',\
                'User_Ecstasy', 'User_Heroin', 'User_Ketamine', 'User_Legalh', 'User_LSD',\
                'User_Meth', 'User_Mushrooms','User_Semer', 'User_VSA']

def make_cumvar (list):
    User_cum = ['Non-user'] * len(PsychDrug)
#    User_cum = [False] * len(PsychDrug)
    for i in range(len(PsychDrug)):
        for drug in list:
            if PsychDrug[drug][i]==True:
                User_cum[i] = 'User'
#                User_cum[i] = True
    return User_cum

PsychDrug['User_LegalDrugs'] = make_cumvar(LegalDrugs)
PsychDrug['User_IllegalDrugs'] = make_cumvar(IllegalDrugs)

# Visualization of a continous variable for certain groups
# For example: Big Five scores for users and non-users of illegal drugs in comparison

NonUser = mpatches.Patch(color='blue')
User = mpatches.Patch(color='red')
mypal = {'Non-user': 'b', 'User': 'r'}

f, axes = plt.subplots(5, 1, sharex=True, sharey=True)
f.subplots_adjust(hspace=.75)

sns.boxplot(x = 'Nscore', y = 'User_IllegalDrugs', data = PsychDrug, ax = axes[0], palette = mypal)
sns.boxplot(x = 'Escore', y = 'User_IllegalDrugs', data = PsychDrug, ax = axes[1], palette = mypal)
sns.boxplot(x = 'Oscore', y = 'User_IllegalDrugs', data = PsychDrug, ax = axes[2], palette = mypal)
sns.boxplot(x = 'Ascore', y = 'User_IllegalDrugs', data = PsychDrug, ax = axes[3], palette = mypal)
sns.boxplot(x = 'Cscore', y = 'User_IllegalDrugs', data = PsychDrug, ax = axes[4], palette = mypal)
f.legend(handles = [NonUser,User], labels = ['Non-user','User'], loc = 'lower right')
f.suptitle('Big Five for users and non-users of illegal drugs (decade-based)')

for boxplot in range(5):
    axes[boxplot].yaxis.set_visible(False)
#%%
#----------------------------------3. Bayesian Network with pomegranate--------------------

def prediction_matrix(model, X_test, y_test):
    # rename X_test columns to fit to model nodes
    X_test_nodes = X_test.round() # Discretization
    X_test_nodes.columns = [str(no) for no in np.arange(len(X_test_nodes.columns))]
    
    y_pred = []
    # loop over all record in the X_test_nodes nodes (where each record is one dictionary)
    for record in X_test_nodes.to_dict('records'):
        prediction = model.predict_proba(record)

        record_pred = []
        for i in range(len(y_test.columns)):
            no_node = len(X_test.columns) + i
            record_pred.append(prediction[no_node].parameters[0][1])
            
        #print(record_pred)
        y_pred.append(record_pred)
    
    y_pred = pd.DataFrame(y_pred, columns=[DrugVar]).set_index(y_test.index)
    
    return y_pred
       

def prediction_metrics(drug, y_pred, y_test):
    predicted_values = y_pred[[drug]].round().values.tolist()
    true_values = y_test[drug].tolist()
    
    confusion_matrix = metrics.confusion_matrix(true_values, predicted_values)
    sensitivity = confusion_matrix[0,0] / (confusion_matrix[0,0] + confusion_matrix[1,0]) # TP / (TP + FN)
    specifity = confusion_matrix[1,1] / (confusion_matrix[0,1] + confusion_matrix[1,1]) # TN / (TN + FP)
    
    print("Confusion_matrix:\n", confusion_matrix,
          "\nAccuracy: ", metrics.accuracy_score(true_values, predicted_values).round(2),
          "\nSensitivity: ", round(sensitivity, 2),
          "\nSpecifity: ", round(specifity, 2))

#----------------------------------3.1 Discretization--------------------------------

discretizer = KBinsDiscretizer(n_bins=8, encode='ordinal', strategy='quantile')
discretizer.fit(PsychDrug[['Nscore','Escore','Oscore','Ascore','Cscore', 'Impulsiv', 'SS']])
var_discretized = discretizer.transform(PsychDrug[['Nscore','Escore','Oscore','Ascore','Cscore', 'Impulsiv', 'SS']])
var_discretized = pd.DataFrame(var_discretized, 
                               columns=['Nscore_d','Escore_d','Oscore_d','Ascore_d','Cscore_d', 'Impulsiv_d', 'SS_d'])

# Example frequencies
var_discretized.groupby('Impulsiv_d').size()

# Join of discretized variables on PsychDrug
PsychDrug = PsychDrug.join(var_discretized)

# Plot to view distribution of Nscore
sns.scatterplot(PsychDrug['Nscore_d'], PsychDrug['Nscore'])

#----------------------------------3.1 Initialization, Split into Training & Test Data--------------------

DemoVar = ['Education','Gender', 'Age']
#Big5Var = ['Nscore','Escore','Oscore','Ascore','Cscore'] #+ ['Impulsiv', 'SS']
Big5Var = ['Nscore_d','Escore_d','Oscore_d','Ascore_d','Cscore_d'] #+ ['Impulsiv_d', 'SS_d']
DrugVar = ['User_LSD', 'User_Alcohol']

# Split into train and test data
X_train, X_test, y_train, y_test = train_test_split(PsychDrug[DemoVar + Big5Var], 
                                                    PsychDrug[DrugVar], 
                                                    test_size=0.33, 
                                                    random_state=53)

train_df = X_train.join(y_train)

#%%
#----------------------------------3.2 Bayesian Networks with pomegranate ---------------

#----------------------------------3.2.1 Approach 1: Unconstraint learning from data with pomegranate---------------


# Exact learning: Traditional shortest path algorithm
model = BayesianNetwork.from_samples(train_df, algorithm='exact-dp')

# Exact learning: A* algorithm
model = BayesianNetwork.from_samples(train_df, algorithm='exact')

# Approximate learning: Greedy algorithm
model = BayesianNetwork.from_samples(train_df, algorithm='greedy')

# Approximate learning: Chow-Liu tree algorithm
model = BayesianNetwork.from_samples(train_df, algorithm='chow-liu')

model.plot()
model.log_probability(train_df.to_numpy()).sum() 

# Prediction
y_pred = prediction_matrix(model, X_test, y_test)
prediction_metrics('User_LSD', y_pred, y_test)
prediction_metrics('User_Alcohol', y_pred, y_test)


# Dictionary for network nodes to read network structure
for i, var in enumerate(DemoVar+Big5Var+DrugVar):
    print(var, ': ', i)

#%%
#-----------------------------3.2.2 Approach 2: Constrained learning from data with pomegranate--------------------


# Create scaffold of network
demographics = tuple(range(0, len(DemoVar))) #['Education','Gender', 'Age']
psycho_traits = tuple(range(max(demographics) + 1, max(demographics) + len(Big5Var) + 1)) #['Nscore','Escore','Oscore','Ascore','Cscore']
drug_consumption = tuple(range(max(psycho_traits) + 1, max(psycho_traits) + len(DrugVar) + 1)) #['User_LSD', 'User_Alcohol']

# Create network
G = networkx.DiGraph()
G.add_edge(demographics, psycho_traits)
G.add_edge(psycho_traits, psycho_traits) #self-loop
G.add_edge(psycho_traits, drug_consumption)
G.add_edge(drug_consumption, drug_consumption) #self-loop

plot_networkx(G)

# Calculate model
model = BayesianNetwork.from_samples(train_df.to_numpy(), 
                                     algorithm='exact', 
                                     constraint_graph=G)
model.plot()
model.log_probability(train_df.to_numpy()).sum() 

# Prediction of the X_test data
y_pred = prediction_matrix(model, X_test, y_test)
prediction_metrics('User_LSD', y_pred, y_test)
prediction_metrics('User_Alcohol', y_pred, y_test)


#%%
#----------------------------------4. Bayesian Network from scratch--------------------

#----------------------------------4.1 Bayesian Parameter Learning---------------------

#----------------------------------4.2.1. For discrete variables-------------------------

def calc_independent_var_disc(variable):
    parameter = train_df.groupby([variable]).size() / len(train_df[variable])
    return parameter
calc_independent_var_disc('Education')

def calc_cond_prob_disc(y, x1, x_label): # list = [y,x = 'Doctor'] (y has to come first)
    p = train_df.groupby([y, x1]).size() / train_df.groupby(x1).size()  
    return p.filter(like = x_label, axis=0)
calc_cond_prob_disc('User_LSD', 'Education', 'Masters Degree')


#----------------------------------4.2.2. For continuous variables-------------------------


def calc_independent_var_cont(variable):
    avg = np.mean(train_df[variable])
    std = np.std(train_df[variable])
    return avg, std
avg, std = calc_independent_var_cont('Nscore')
norm.logpdf(train_df['Nscore'], loc=avg, scale=std)

# P(y|x) = P(y ∩ x) / P(x) --- Prob with x < 1
def calc_cond_prob_cont(y, y_event, x1, x1_event):
    # P(y ∩ x):
    y_and_x = len(train_df[(train_df[y] == y_event) & (train_df[x1] < x1_event)])
    x = len(train_df[train_df[x1] < x1_event])
    p = y_and_x / x
    return p
calc_cond_prob_cont('User_LSD', True, 'Nscore', 1)


#%%
#----------------------------------4.2 Bayesian Structure Learning---------------------

#----------------------------------4.2.1. For discrete variables-------------------------

train_df_large = train_df
train_df_small = train_df[1:100]
train_df = train_df_small

# Hill-climbing algorithm

def calc_independent_loglikelihood_var_disc(variable):
    x = train_df.groupby([variable]).size()
    n = len(train_df[variable])
    p = x / n
    return np.sum(multinomial.logpmf(x.tolist(),n,p.tolist()))

def calc_cond_prob_loglikelihood_disc(list):
    x = train_df.groupby(list).size()
    p = x / train_df.groupby(list[1:]).size()
    event_combo = x.index.droplevel(0).unique().tolist()
    loglikelihood = 0
    p = p.reorder_levels(order = list)
    x = x.reorder_levels(order = list)
    for elem in event_combo: 
        #print(elem)
        elem = elem if isinstance(elem, tuple) else (elem,)
        x_element = x.loc[(slice(None),) + elem]    # e.g. -> x.loc[slice(None), 'Doctorate Degree', 'Female']
        p_element = p.loc[(slice(None),) + elem]    
        n_element = np.array(x_element).sum()
        loglikelihood += np.sum(multinomial.logpmf(x_element.tolist(), 
                                                   n_element, 
                                                   p_element.tolist()))
    loglikelihood -= (math.log(len(train_df),2)/2)*len(list) # penalty term
    return loglikelihood

def powerset(variables):
    all_combinations = []
    for r in range(1,len(variables)+1):
        combinations_object = combinations(variables, r)
        combinations_list = list(combinations_object)
        all_combinations += combinations_list
        
    return(all_combinations)   

def checking_constraints(child, parents):
    min_num_parents = 0
    max_num_parents = 3
    fits_constraints = False
    
    # setting constraints
    if (len(parents)>min_num_parents) & (len(parents)<max_num_parents):
        # child = DemoVar
        # DemoVar can't have parents of Big5Var or DrugVar
        if (child in DemoVar):
            if (len(set(parents).intersection(DrugVar)) == 0) & (len(set(parents).intersection(Big5Var)) == 0):
                fits_constraints = True
        # child = Big5Var
        # Big5Var can't have parents of DrugVar
        elif (child in Big5Var):
            if len(set(parents).intersection(DrugVar)) == 0:
                fits_constraints = True
        # target_variabe = DrugVar
        # no constraints
        else:
            fits_constraints = True

    return fits_constraints

def calculate_score(structure):
    score = 0
    for key, value in structure.items():
        list_cond = []
        if value == '':
            score += calc_independent_loglikelihood_var_disc(key)
        else:
            list_cond.append(key)
            for val in value:
                list_cond.append(val)
            score += calc_cond_prob_loglikelihood_disc(list_cond)
    return score

def generate_new_structure(structure, child, parents):
    structure[child] = parents
    for variable in parents:
        for key, value in structure.items():
            if (key == variable) & (value == ''):
                structure.pop(variable, None)
                break
    return structure

def hill_climbing_algorithm(target_variable):
    iteration = 0
    score = NEGINF
    structure = {}
    history = []
    # Initializing structure with all independent nodes
    variable_list = [target_variable] + Big5Var + DemoVar
    for variable in variable_list:
        structure[variable] = ''
    score = calculate_score(structure)
    # Creating list with child-nodes
    list_children = variable_list.copy()
    # Going through every y in P(y|x1,x2...)
    while list_children != []:
        list_parents = variable_list.copy()
        initial_structure = structure
        # Checking possible parents for target_variable, then random choice
        if iteration == 0:
            target = target_variable
        else:
            target = np.random.choice(list_children)
        list_parents.remove(target)
        list_children.remove(target)
        # Going through every x in P(y|x1,x2)
        for combo in powerset(list_parents):
            if checking_constraints(target, combo) == True:
                structure_new = generate_new_structure(initial_structure.copy(), target, combo)
                score_new = calculate_score(structure_new)
                history.append((str(target), combo))
                if score_new > score:
                    score = score_new
                    structure = structure_new
                    history.append(((target, combo), structure,score))
        iteration = iteration + 1
    return structure, history
    
result1, history = hill_climbing_algorithm('User_LSD')


#----------------------------------4.2.2. For continuous variables-------------------------

def calc_independent_loglikelihood_var_cont(variable):
    avg = np.mean(PsychDrug[variable])
    std = np.std(PsychDrug[variable])
    return np.sum(norm.logpdf(PsychDrug[variable], avg, std))

likelihood = calc_independent_loglikelihood_var_cont('Oscore')

# Imported from https://github.com/darshanbagul/BayesianNetworks/blob/master/report_utils.py
def calc_cond_prob_one_var_cont(y, x):
    #x = PsychDrug['Oscore']
    #y = PsychDrug['Escore']
    sq_temp = np.dot(x, np.vstack(x)) # temp^2 = x^T * x
    l1 = [len(x) , np.sum(x)]
    l2 = [np.sum(x), sq_temp[0]]
    A = np.vstack([l1, l2])
    y_mod = [np.sum(y), np.dot(x,y)]

    A_inv = np.linalg.inv(A)
    B  = np.dot(A_inv, y_mod)

    var_temp = 0
    for i in range(len(y)):
        var_temp += np.square((B[0] + (B[1] * x[i])) - y[i])

    var = var_temp/len(y)
    sigma = np.sqrt(var)
    log_likelihood = 0
    for i in range(len(y)):
        log_likelihood += norm.logpdf(y[i], B[0]+B[1]*x[i], sigma)
    return log_likelihood

likelihood = calc_cond_prob_one_var_cont(train_df["Escore"], train_df["Oscore"])

# Testing
a = np.array(PsychDrug['Escore'])
b = np.array(PsychDrug['Oscore'])
test = np.row_stack((b,a))
np.cov(test)

#----------------------------------4.2.3. For mixed variables-------------------------

# L(data|model) = L(P(y|x)|model) where y is discrete and x is continuous
