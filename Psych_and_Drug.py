# -*- coding: utf-8 -*-
'''
Course: Machine Learning Lab given by Prof. Brefeld
Project: Influence of psychological factors on drug consumption
Authors: Johanna Regenthal and Sofija Engelson
Due date: 
'''
#%%
# ---------- 0.Preliminaries -------------------------------------------------

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency, norm, multinomial, stats
from matplotlib import patches as mpatches
from pomegranate import *
from pomegranate.utils import plot_networkx
import networkx
from itertools import combinations, chain
from sklearn.preprocessing import KBinsDiscretizer
import math, copy
import random

# ---------- 1.Reading and cleaning data -------------------------------------

# ---------- 1.1 Reading -----------------------------------------------------

colnames = ['ID','Age','Gender','Education','Country','Ethnicity','Nscore','Escore','Oscore','Ascore','Cscore','Impulsiv','SS','Alcohol','Amphet','Amyl','Benzos','Caff','Cannabis','Choc','Coke','Crack','Ecstasy','Heroin','Ketamine','Legalh','LSD','Meth','Mushrooms','Nicotine','Semer','VSA']

PsychDrug = pd.read_csv('drug_consumption.data', names = colnames, header = None)
PsychDrug.head()

# ---------- 1.2 Cleaning ----------------------------------------------------

# ---------- 1.2.1 Classification into Users and Non-users for all drugs------
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

# ---------- 1.2.2 Dequantification of explanatory variables -----------------

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

DemoVar = ['Education','Gender', 'Age']
Big5Var = ['Nscore','Escore','Oscore','Ascore','Cscore'] #+ ['Impulsiv', 'SS']
DrugVar = ['User_LSD', 'User_Alcohol']

#%%

# ---------- 2. Exploratory analysis -----------------------------------------
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

# ---------- 2.1 Correletions ------------------------------------------------

# Cramer's V for correlation between two categorical variables (demographic variable --> usage classification)
# Imported from: https://stackoverflow.com/questions/20892799/using-pandas-calculate-cram%C3%A9rs-coefficient-matrix

def cramers_corrected_stat(v1,v2):
    """ calculate Cramers V statistic for categorial-categorial association.
        uses correction from Bergsma and Wicher, 
        Journal of the Korean Statistical Society 42 (2013): 323-328
    """
    confusion_matrix = pd.crosstab(PsychDrug[v1], PsychDrug[v2], margins = False)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2/n
    r,k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))    
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    return np.sqrt(phi2corr / min( (kcorr-1), (rcorr-1)))

def calculate_CramersV():
    CramersV_df = pd.DataFrame(DemoVar, columns = ['Variable'])
    for drug in DrugVar:
        CramersV = []
        for variable in DemoVar:
            CramersV.append(cramers_corrected_stat(drug, variable))
        CramersV_df[drug] = CramersV
    return(CramersV_df)

print(calculate_CramersV())

# Biserial correlation between a binary and a numerical variable (Big5Var --> DrugVar)
# For example: Oscore and usage of LSD

def calculate_biserial_correlation():
    BisCor_df = pd.DataFrame(Big5Var, columns = ['Variable'])
    for drug in DrugVar:
        Cor_list = []
        for variable in Big5Var:
            Cor = stats.pointbiserialr(PsychDrug[drug], PsychDrug[variable])[0] 
            pvalue = stats.pointbiserialr(PsychDrug[drug], PsychDrug[variable])[1]
            if pvalue < 0.05:
                Cor_list.append(Cor)
            else:
                Cor_list.append(0)
        BisCor_df[drug] = Cor_list
    return BisCor_df

print(calculate_biserial_correlation())
    
# ---------- 2.2 Visualization of users and non-users -------------------------

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
# ---------- 3. Bayesian Network with pomegranate ----------------------------

def prediction_pomegranate(model, X_test, y_test):
    # rename X_test columns to fit to model nodes
    X_test_nodes = X_test.copy() 
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
          "\nSpecificity: ", round(specifity, 2))

# ---------- 3.1. Discretization ----------------------------------------------

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

#%%
# ---------- 3.2. Split into Training & Test Data ----------------------------

#Big5Var = ['Nscore_d','Escore_d','Oscore_d','Ascore_d','Cscore_d'] #+ ['Impulsiv_d', 'SS_d']
Big5Var = ['Nscore','Escore','Oscore','Ascore','Cscore'] #+ ['Impulsiv', 'SS']

# Split into train and test data
X_train, X_test, y_train, y_test = train_test_split(PsychDrug[DemoVar + Big5Var], 
                                                    PsychDrug[DrugVar], 
                                                    test_size=0.33, 
                                                    random_state=53)

train_df = X_train.join(y_train)
test_df = X_test.join(y_test)

#%%
# ---------- 3.3. Training a Bayesian Networks with pomegranate ---------------

# ---------- 3.3.1 Approach 1: Unconstraint learning from data with pomegranate---

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
y_pred = prediction_pomegranate(model, X_test, y_test)
prediction_metrics('User_LSD', y_pred, y_test)
prediction_metrics('User_Alcohol', y_pred, y_test)


# Dictionary for network nodes to read network structure
for i, var in enumerate(DemoVar+Big5Var+DrugVar):
    print(var, ': ', i)
    
#%%
# ---------- 3.3.2 Approach 2: Constrained learning from data with pomegranate---

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
y_pred = prediction_pomegranate(model, X_test, y_test)
prediction_metrics('User_LSD', y_pred, y_test)

#%%
# ---------- 4. Bayesian Network from scratch --------------------------------

# ---------- 4.1 Likelihood Calculation --------------------------------------

def calc_independent_loglikelihood_var_disc(variable):
    x = train_df.groupby([variable]).size()
    n = len(train_df[variable])
    p = x / n
    loglike_array = multinomial.logpmf(x.tolist(), n, p.tolist())
    loglikelihood = np.sum(loglike_array)
    return loglikelihood

def calc_independent_loglikelihood_var_cont(variable):
    #avg = np.mean(train_df[variable])
    #std = np.std(train_df[variable])
    avg, std = norm.fit(train_df[variable])
    loglikelihood = np.sum(norm.logpdf(train_df[variable], avg, std))
    return loglikelihood

def calc_cond_prob_loglikelihood_disc(variables):
    loglikelihood = 0
    x = train_df.groupby(variables).size()
    p = x / train_df.groupby(variables[1:]).size()
    event_combo = x.index.droplevel(0).unique().tolist()
    p = p.reorder_levels(order = variables)
    x = x.reorder_levels(order = variables)
    for elem in event_combo: 
        #print(elem)
        elem = elem if isinstance(elem, tuple) else (elem,)
        x_element = x.loc[(slice(None),) + elem]    # e.g. -> x.loc[slice(None), 'Doctorate Degree', 'Female']
        p_element = p.loc[(slice(None),) + elem]    
        n_element = np.array(x_element).sum()
        loglikelihood += np.sum(multinomial.logpmf(x_element.tolist(), 
                                                   n_element, 
                                                   p_element.tolist()))
    #loglikelihood -= (math.log(len(train_df),2)/2)*len(variables) # penalty term
    return loglikelihood

# Implementation of Conditional Gaussians
    # Based on https://par.nsf.gov/servlets/purl/10048513
def calc_cond_loglikelihood(variables):
#variables = ['Nscore', 'Oscore']

    y = variables[0]
    parents = variables[1:]
    parents_d = []
    parents_c = []
    loglikelihood = 0
    
    # Create parent sets partitioned by continuous and discrete variables
    for parent in parents:
        if parent in ['Nscore','Escore','Oscore','Ascore','Cscore', 'Impulsiv', 'SS']:
            parents_c.append(parent)
        else:
            parents_d.append(parent)
    
    # Check if y is continuous and discrete variables
    if y in ['Nscore','Escore','Oscore','Ascore','Cscore', 'Impulsiv', 'SS']:
        y_continuous = True
    else:
        y_continuous = False
            
    # if all variables are discrete
    if (len(parents_c) == 0) and (y_continuous == False):
        X = train_df.groupby(variables).size()
        N = len(train_df)
        
        # with PMF & loglikelihood
        P = X / N
        loglike_array = multinomial.logpmf(X.tolist(), N, P.tolist())
        loglikelihood = np.sum(loglike_array)

    # if all variables are continuous
    elif len(parents_d) == 0 and (y_continuous == True):
        X = train_df[parents_c + [y]]
        n, k = X.shape
        # Parameter estimation with MLE for each parent_c
        #mu_vec = []
        sigma_vec = []
        for var in X.columns:
            mean, variance = norm.fit(X[var]) #MLE
            #mu_vec.append(mean)
            sigma_vec.append(variance)
        sigma_array = np.array(sigma_vec)
        # Calculate Likelihood with Formula
        loglike_c = -(n / 2) * (np.log(abs(sigma_array)) + k * np.log(2 * math.pi) + 1)
        loglikelihood = loglike_c.sum()

    # else: mixed case    
    else:
        # Partitioning
        if y_continuous:
            X = train_df.set_index(parents_d)[parents_c + [y]]
        else:
            X = train_df.set_index(parents_d + [y])[parents_c]
        pi_i = X.index.unique().tolist()
        
        # Iterate over partitions
        for p in pi_i:
            # Create design matrix for partition p
            X_p = X.loc[p]
            n, k = X_p.shape
            # Parameter estimation with MLE for each parent_c
            #mu_vec = []
            sigma_vec = []
            for var in X_p.columns:
                mean, variance = norm.fit(X_p[var]) #MLE
                #mu_vec.append(mean)
                sigma_vec.append(variance)
            sigma_array = np.array(sigma_vec)
            # Calculate Likelihood with Formula
            loglike_c = -(n / 2) * (np.log(abs(sigma_array)) + k * np.log(2 * math.pi) + 1)
            loglike_d = n * np.log(n / len(train_df))
            loglikelihood += loglike_c + loglike_d
    # Calculate likelihood of parents
    loglike_parents = 0
    for parent in parents:
        if parent in parents_c:
            loglike_parents += calc_independent_loglikelihood_var_cont(parent)
        else:
            loglike_parents += calc_independent_loglikelihood_var_disc(parent)
    loglikelihood = loglikelihood.sum() - loglike_parents.sum()
    
    return loglikelihood

#%%
# ---------- 4.2 Bayesian Structure Learning ---------------------------------

# ---------- 4.2.1 For discrete variables ------------------------------------

#train_df_large = train_df
#train_df_small = train_df[1:100]
#train_df = train_df_small
#train_df = train_df_large

# Hill-climbing algorithm

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
            score += calc_cond_loglikelihood(list_cond)
            #score += calc_cond_prob_loglikelihood_disc(list_cond)
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
    random.seed(123)
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
                if score_new > score:
                    score = score_new
                    structure = structure_new
                    history.append(('update', (str(target), combo), structure, score))
                else:
                    history.append(('no update', (str(target), combo), score_new))
        iteration = iteration + 1
    return structure, history
    
result1, history = hill_climbing_algorithm('User_LSD')

for line in history:
    print(line)

# TESTING
# Plotting different Likelihoods
variables = ['User_LSD', 'Oscore_d', 'Education']
variables = 'User_LSD'
variables = ['Oscore', 'Nscore', 'Escore']

x = []
y = []
for i in range(100,1300,100):
    train_df_small = train_df_large[1:i]
    train_df = train_df_small
    x.append(i)
    logli = calc_cond_loglikelihood(variables)
    #logli = calc_cond_prob_loglikelihood_disc(variables)
    #logli = calc_independent_loglikelihood_var_disc(variables)
    y.append(logli)
    print('parents: ', len(variables)-1, 'datapoints: ', i , ' , ', logli)

                                       
plt.scatter(x,y)
plt.title(str(variables))
plt.show()


#%%
# ---------- 4.3. Probabilistic Inference ------------------------------------

def ind_prob_table_discrete(df, variable):
    parameter = df.groupby([variable]).size() / len(df[variable])
    return parameter
#Example: ind_prob_table_discrete(test_df, 'User_LSD')

def cond_prob_table_discrete(df, targetvariable, parents):
    variable_list = [targetvariable] + parents
    x = df.groupby(variable_list).size()
    parameter = x / df.groupby(variable_list[1:]).size()
    parameter = parameter.reorder_levels(order = variable_list)
    return parameter
#Example: cond_prob_table_discrete(test_df, 'User_LSD', list(result1['User_LSD']))

def ind_prob_parameter_continuous(df, targetvariable):
    avg, std = norm.fit(df[targetvariable])
    #prob = norm.pdf(x, avg, std)
    return avg, std
#Example: ind_prob_parameter_continuous(df, 'Nscore')

# https://stats.libretexts.org/Bookshelves/Probability_Theory/Book%3A_Introductory_Probability_(Grinstead_and_Snell)/04%3A_Conditional_Probability/4.02%3A_Continuous_Conditional_Probability
# targetvariable is continuous
def cond_prob_parameter_continuous(df, targetvariable, parents, e):
    X = df.set_index(parents)[targetvariable]
    filtering = tuple(e[parents])
    avg, std = norm.fit(X[filtering])
    return avg, std


#%%
# ---------- 4.3.1 Inference with Enumerate Algorithm ------------------------

# Variable Enumeration Algorithm
# Based on:
    # http://courses.csail.mit.edu/6.034s/handouts/spring12/bayesnets-pseudocode.pdf
    # https://www.ke.tu-darmstadt.de/lehre/archiv/ws-14-15/ki/bayesian-networks2.pdf
    # https://github.com/sonph/bayesnetinference/blob/master/BayesNet.py

def topological_order(result, target_variable):
    variables = list(result.keys())
    all_parents = [list(result[key]) for key, val in result.items() if val != '']
    for parents in all_parents:
        for parent in parents:
            if parent not in variables:
                variables.insert(0, parent)
    return variables

def query_prob(result, Y, y, e):
    """
        Query P(Y | e), or the probability of the variable `Y`, given the
        evidence set `e`, extended with the value of `Y`. All immediate parents
        of Y have to be in `e`.
    """
#result = result1
#Y = 'User_LSD'
#y = True
#e = X_test.iloc[0,][Big5Var + DemoVar]
    
    # if Y is continuous (with discrete parents)
    if Y in ['Nscore','Escore','Oscore','Ascore','Cscore', 'Impulsiv', 'SS']:
        # heck if variable has parents
        if Y in result.keys():
            if result[Y] != '':
                parents = list(result[Y])
                avg, std = cond_prob_parameter_continuous(train_df, Y, parents, e)
                ret = norm.pdf(y, avg, std)
            else: 
                avg, std = ind_prob_parameter_continuous(train_df, Y)
                ret = norm.pdf(y, avg, std)
        else: 
            avg, std = ind_prob_parameter_continuous(train_df, Y)
            ret = norm.pdf(y, avg, std)
    
            
    # if Y is discrete (with discrete paretns)
    else: 
        # Check if variable has parents
        if Y in result.keys():
            if result[Y] != '':
                parents = list(result[Y])
                cpt = cond_prob_table_discrete(train_df, Y, parents)
                cpt = cpt.reorder_levels(order = [Y] + parents)
                try:
                    ret = cpt.loc[(y,) + tuple(e[parents])]
                except KeyError:
                    ret = 0
            else: 
                cpt = ind_prob_table_discrete(test_df, Y)
                ret = cpt.loc[(y,)]
        else: 
            cpt = ind_prob_table_discrete(test_df, Y)
            ret = cpt.loc[(y,)]
    return ret
    
def enumerate_all(result, variables, e):
#result = result1
#variables = ['Education','Oscore_d','User_LSD']
#e = X_test.iloc[0,][Big5Var + DemoVar]
    if len(variables) == 0:
        return 1
    Y = variables[0]
    # If y is part of e, return the (cond.) probability
    if Y in e.index:
        y = e[Y]
        ret = query_prob(result, Y, y, e) #* enumerate_all(result, variables[1:], e)
    # If y is not part of e
    else:
        print(Y, ' not part of e')
        probs = []
        e_y = copy.deepcopy(e)
        # Loop over all possible answers of y
        for y in PsychDrug[Y].unique():
            e_y[Y] = y
            probs.append(query_prob(result, Y, y, e_y)) #* enumerate_all(result, variables[1:], e)
        ret = sum(probs)
    return ret

def enumerate_ask(X, e, result):
#X = 'User_LSD' # Target Variable
#e = X_test.iloc[-2,][Big5Var + DemoVar]
    # Initialization of distribution of target variable X
    Q = pd.Series([])
    # For each possible value x that X can have
    for x in PsychDrug[X].unique():
        # extend evidence e with value of X
        e = copy.deepcopy(e)
        e[X] = x
        # sort variables in topological order
        variables = topological_order(result, X) 
        # Calculate enumeration
        prob = 1
        while len(variables) > 0:
            prob = enumerate_all(result, variables, e) * prob
            variables.pop(0)
        Q[str(x)] = prob
    # Normalization
    Q = Q / sum(Q)
    return Q
        
def prediction_scratch_enumerate(test_df, result, X):
    y_pred = []
    for row_index, record in test_df.iterrows():
        e = copy.deepcopy(record)
        Q = enumerate_ask(X, e, result)
        record_pred = Q['True']
        y_pred.append(record_pred)        
    y_pred = pd.DataFrame(y_pred, columns=[X]).set_index(y_test.index)
    return y_pred


y_pred = prediction_scratch_enumerate(test_df, result1, 'User_LSD')
prediction_metrics('User_LSD', y_pred, y_test)

#%%
# ---------- Results with pomegranate structure -------------------------------

# Create dictionary for Variables
dictionary = {}
for i, var in enumerate(DemoVar+Big5Var+DrugVar):
    dictionary[i] = var

# Create structure format 
structure = {}
for i, node in enumerate(model.structure):
    child = dictionary[i]
    if len(node) == 0:
        parents = ''
    else:
        parents = ()
        for j in node:
            parents += (dictionary[j],)
    structure[child] = parents

structure.pop('Gender', None)
structure.pop('Oscore_d', None)
structure.pop('User_Alcohol', None)

y_pred = prediction_scratch_enumerate(test_df, structure, 'User_LSD')
prediction_metrics('User_LSD', y_pred, y_test)

