#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 15:42:23 2025

@author: tbj
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from tqdm import tqdm
import re
from sklearn.utils import resample


df_2012_author = pd.read_csv('2012 ANES.csv')
df_2016_author = pd.read_csv('2016 ANES.csv')
df_2020_author = pd.read_csv('2020 ANES.csv')



df_2012 = pd.read_csv('anes_2012_original.csv')
df_2016 = pd.read_csv('anes_2016_original.csv')
df_2020 = pd.read_csv('anes_2020_original.csv')
df_2020 = df_2020[df_2020['V200001'].isin(df_2020_author['V200001'])]

df_list = [df_2012, df_2016, df_2020]
df_year = ['2012', '2016', '2020']

def select_variables(df_list,df_year):
    
    var_2012 = ['CASEID','DEM_RACEETH_X','DISCUSS_DISC','PID_X','RELIG_CHURCH','DEM_AGE_R_X','GENDER_RESPONDENT_X',
                    'PAPROFILE_INTERESTPOLIT','SAMPLE_REGION','INTEREST_FOLLOWING','CONGAPP_JOB','PRESAPP_TRACK',
                    'FINANCE_FINFAM','FINANCE_FINPAST_X','FINANCE_FINNEXT_X','HEALTH_SELF','INEQ_INCGAP','PRESWIN_DUTYCHOICE_X',
                    'GUN_CONTROL','IMMIG_POLICY','FEDSPEND_WELFARE','FEDSPEND_ENVIRO','TRUST_SOCIAL','RESPONS_ELECTIONS',
                    'GAYRT_DISCREV','ABORTPRE_4POINT','RELIG_WORDGOD','DEM_UNIONHH','ORIENTN_RGAY','HAPP_LIFESATISF']
    var_2016 = ['V160001','V161310X','V162174','V161158X','V161244','V161267','V161342',
                    'V162256','V161010D','V161004','V161080','V161081','V161109',
                    'V161110','V161111','V161115','V161137','V161151X','V161187',
                    'V161192','V161209','V161212','V161219','V161220','V161229',
                    'V161232','V161243','V161302','V161511','V161522']
    var_2020 = ['V200001','V201549X','V202022','V201231X','V201452','V201507X','V201600',
                    'V202406','V203003','V201006','V201124','V201114','V201501',
                    'V201502','V201503','V201623','V201397','V201225X','V202337',
                    'V201417','V201312','V201321','V201237','V201238','V201412',
                    'V201336','V201434','V201544','V201601','V201651']
    renamed_var = ['id','race','discuss_politics','ideology','attend_church','age','gender',
                    'political_interest','region','campaign_interest','congress_approval','country_track',
                    'family_num','finance_past','finance_next','health','inequality_gap','voting_duty',
                    'gun_control','immigration_policy','welfare_spend','environment_protection','trust','election_impact',
                    'gay_protection','abortion_legality','bible_truth','union_membership',
                    'sexual_orientation','life_satisfaction']
    dfs = []
    for df, year in zip(df_list, df_year):
        if year == '2012':
            df = df[var_2012]
            df.columns = renamed_var
            dfs.append(df)
        elif year == '2016':
            df = df[var_2016]
            df.columns = renamed_var
            dfs.append(df)
        elif year == '2020':
            df = df[var_2020]
            df.columns = renamed_var
            dfs.append(df)
    return dfs

df_renamed_list = select_variables(df_list, df_year)
df_2012,df_2016,df_2020 = df_renamed_list

def no_dummy_name(feature_list):
    cleaned = []
    for var in feature_list:
        cleaned_name = re.sub(r'_(\d+(\.\d+)?)$', '', var)
        cleaned.append(cleaned_name)
    return cleaned

def redefine_variable(df_list,df_year,rf_short_long,features_2012_attend_church=None,
                      features_2012_discuss_politics=None,
                      features_2012_political_interest=None,
                      features_2016_attend_church=None,
                      features_2016_discuss_politics=None,
                      features_2016_political_interest=None,
                      features_2020_attend_church=None,
                      features_2020_discuss_politics=None,
                      features_2020_political_interest=None):
    if rf_short_long == 'rf':
        dfs = []
        for df,year in zip(df_list,df_year):
            df['race'] = df['race'].replace(6, np.nan)
            df['abortion_legality'] = df['abortion_legality'].replace(5, np.nan)
            df['bible_truth'] = df['bible_truth'].replace(5, np.nan)
            df['gun_control'] = df['gun_control'].map({2:3,3:2}).fillna(df['gun_control'])
            df['welfare_spend'] = df['welfare_spend'].map({2:3,3:2}).fillna(df['welfare_spend'])
            df['environment_protection'] = df['environment_protection'].map({2:3,3:2}).fillna(df['environment_protection'])
            if year == '2016':
                df['gender'] = df['gender'].replace(3, np.nan)
                df['region_2'] = df['region'].isin([17, 18, 19, 20, 26, 27, 29, 31, 38, 39, 46, 55])
                df['region_3'] = df['region'].isin([1, 5, 12, 13, 21, 22, 24, 28, 37, 40, 45, 47, 48, 51, 54])
                df['region_4'] = df['region'].isin([2, 4, 6, 8, 15, 16, 30, 32, 35, 41, 49, 53, 56])
                df = df.drop(columns=['region'])
                df[df < 0] = pd.NA
                df = df.dropna()
                df = pd.get_dummies(df, columns=['gender', 'congress_approval', 'country_track',
                                    'gay_protection','sexual_orientation','race'], drop_first=True)
                df.iloc[:, 23:] = df.iloc[:, 23:].astype(int)
                dfs.append(df)
            if year == '2020':
                df['race'] = df['race'].map({3:4,4:3}).fillna(df['race'])
                df['sexual_orientation'] = df['sexual_orientation'].replace(4,np.nan)
            if year == '2012' or year == '2020':
                df[df < 0] = pd.NA
                df = df.dropna()
                df = pd.get_dummies(df, columns=['gender', 'congress_approval', 'country_track','region',
                                     'gay_protection','sexual_orientation','race'], drop_first=True)
                df.iloc[:, 23:] = df.iloc[:, 23:].astype(int)
                dfs.append(df)
        return dfs
    
    if rf_short_long != 'rf':
        features_2012_attend_church = no_dummy_name(features_2012_attend_church)
        features_2012_discuss_politics = no_dummy_name(features_2012_discuss_politics)
        features_2012_political_interest = no_dummy_name(features_2012_political_interest)
        features_2016_attend_church = no_dummy_name(features_2016_attend_church)
        features_2016_discuss_politics = no_dummy_name(features_2016_discuss_politics)
        features_2016_political_interest = no_dummy_name(features_2016_political_interest)
        features_2020_attend_church = no_dummy_name(features_2020_attend_church)
        features_2020_discuss_politics = no_dummy_name(features_2020_discuss_politics)
        features_2020_political_interest = no_dummy_name(features_2020_political_interest)
                 
    if rf_short_long == 'short':
       attend_church_2012_short = df_2012[[df_2012.columns[0], 'attend_church'] + features_2012_attend_church[:10]]
       attend_church_2012_short = attend_church_2012_short.drop(rf_2012.index)
       discuss_politics_2012_short = df_2012[[df_2012.columns[0], 'discuss_politics'] + features_2012_discuss_politics[:10]]
       discuss_politics_2012_short = discuss_politics_2012_short.drop(rf_2012.index)
       political_interest_2012_short = df_2012[[df_2012.columns[0], 'political_interest'] + features_2012_political_interest[:10]]
       political_interest_2012_short = political_interest_2012_short.drop(rf_2012.index)
       
       
       attend_church_2016_short = df_2016[[df_2016.columns[0], 'attend_church'] + features_2016_attend_church[:10]]
       attend_church_2016_short = attend_church_2016_short.drop(rf_2016.index)
       discuss_politics_2016_short = df_2016[[df_2016.columns[0], 'discuss_politics'] + features_2016_discuss_politics[:10]]
       discuss_politics_2016_short = discuss_politics_2016_short.drop(rf_2016.index)
       political_interest_2016_short = df_2016[[df_2016.columns[0], 'political_interest'] + features_2016_political_interest[:10]]
       political_interest_2016_short = political_interest_2016_short.drop(rf_2016.index)
       
       
       attend_church_2020_short = df_2020[[df_2020.columns[0], 'attend_church'] + features_2020_attend_church[:10]]
       attend_church_2020_short = attend_church_2020_short.drop(rf_2020.index)
       discuss_politics_2020_short = df_2020[[df_2020.columns[0], 'discuss_politics'] + features_2020_discuss_politics[:10]]
       discuss_politics_2020_short = discuss_politics_2020_short.drop(rf_2020.index)
       political_interest_2020_short = df_2020[[df_2020.columns[0], 'political_interest'] + features_2020_political_interest[:10]]
       political_interest_2020_short = political_interest_2020_short.drop(rf_2020.index)
      
       return [attend_church_2012_short, discuss_politics_2012_short, political_interest_2012_short,
            attend_church_2016_short, discuss_politics_2016_short, political_interest_2016_short,
            attend_church_2020_short, discuss_politics_2020_short, political_interest_2020_short]
       

    if rf_short_long == 'long':
       attend_church_2012_long = df_2012[[df_2012.columns[0], 'attend_church'] + features_2012_attend_church]
       attend_church_2012_long = attend_church_2012_long.drop(rf_2012.index)
       discuss_politics_2012_long = df_2012[[df_2012.columns[0], 'discuss_politics'] + features_2012_discuss_politics]
       discuss_politics_2012_long = discuss_politics_2012_long.drop(rf_2012.index)
       political_interest_2012_long = df_2012[[df_2012.columns[0], 'political_interest'] + features_2012_political_interest]
       political_interest_2012_long = political_interest_2012_long.drop(rf_2012.index)
       
       attend_church_2016_long = df_2016[[df_2016.columns[0], 'attend_church'] + features_2016_attend_church]
       attend_church_2016_long = attend_church_2016_long.drop(rf_2016.index)
       discuss_politics_2016_long = df_2016[[df_2016.columns[0], 'discuss_politics'] + features_2016_discuss_politics]
       discuss_politics_2016_long = discuss_politics_2016_long.drop(rf_2016.index)
       political_interest_2016_long = df_2016[[df_2016.columns[0], 'political_interest'] + features_2016_political_interest]
       political_interest_2016_long = political_interest_2016_long.drop(rf_2016.index)
       
       attend_church_2020_long = df_2020[[df_2020.columns[0], 'attend_church'] + features_2020_attend_church]
       attend_church_2020_long = attend_church_2020_long.drop(rf_2020.index)
       discuss_politics_2020_long = df_2020[[df_2020.columns[0], 'discuss_politics'] + features_2020_discuss_politics]
       discuss_politics_2020_long = discuss_politics_2020_long.drop(rf_2020.index)
       political_interest_2020_long = df_2020[[df_2020.columns[0], 'political_interest'] + features_2020_political_interest]
       political_interest_2020_long = political_interest_2020_long.drop(rf_2020.index)

       
       return [attend_church_2012_long, discuss_politics_2012_long, political_interest_2012_long,
            attend_church_2016_long, discuss_politics_2016_long, political_interest_2016_long,
            attend_church_2020_long, discuss_politics_2020_long, political_interest_2020_long]

                
df_cleaned_list = redefine_variable(df_renamed_list, df_year,rf_short_long='rf')


rf_input = []
#gpt_input = []
for df in df_cleaned_list:
    target_var = df.columns[1] 
    
    df_rf = df.groupby(target_var, group_keys=False).apply(lambda x: x.sample(frac=0.5, random_state=3))
    
   # df_gpt = df.drop(df_rf.index)
    
    rf_input.append(df_rf)
    #gpt_input.append(df_gpt)


#df_2012_cleaned,df_2016_cleaned,df_2020_cleaned =df_cleaned_list
rf_2012,rf_2016,rf_2020 =rf_input


def split_rf(rf_input,df_year):
    feature_importance = {}
    for df, name in tqdm(zip(rf_input, df_year), total=len(rf_input), desc="processing years"):
        df = df.apply(pd.to_numeric, errors='coerce')
        outcome_vars = ['political_interest', 'discuss_politics', 'attend_church']
      #  if name == '2012':
       #     outcome_vars = ['political_interest', 'discuss_politics', 'attend_church']
     #   elif name == '2016':
        #    outcome_vars = ['political_interest', 'discuss_politics', 'attend_church']
        #elif name == '2020':
           # outcome_vars = ['political_interest', 'discuss_politics', 'attend_church']

        for outcome in outcome_vars:
            X = df.drop(columns=[df.columns[0], outcome])
            y = df[outcome]
            
            rf = RandomForestClassifier(n_estimators=500, random_state=1998)
            rf.fit(X, y)
            
            importances = pd.DataFrame({
                'feature': X.columns,
                'importance': rf.feature_importances_
            }).sort_values(by='importance', ascending=False)
            key = f'{name}_{outcome}'
            feature_importance[key] = importances
            
            #feature importance plot
            plt.figure(figsize=(10, 6))
            sns.barplot(x='importance', y='feature', data=importances)
            plt.xlabel('Gini Index', fontsize=14)
            plt.ylabel('')
            plt.tick_params(axis='x', labelsize=12)
            
            plt.axhline(y=9.5, color='red', linestyle='--', linewidth=1) 
            plt.axhline(y=19.5, color='red', linestyle='--', linewidth=1)
            
            plt.tight_layout()
            
            plot_filename = f'feature_importance_{key}.png'
            plt.savefig(plot_filename)
            plt.close()

            feature_importance[f'{name}_{outcome}'] = importances.head(20)
     
    all_features = {}
    for key, df in feature_importance.items():
        feature_list = df['feature'].tolist()
        all_features[key] = feature_list
        for key, features in all_features.items():
            var_name = f"features_{key}"
            globals()[var_name] = features

            
split_rf(rf_input,df_year)

llm_short = redefine_variable(df_list,df_year,'short',features_2012_attend_church=features_2012_attend_church,
    features_2012_discuss_politics=features_2012_discuss_politics,
    features_2012_political_interest=features_2012_political_interest,
    features_2016_attend_church=features_2016_attend_church,
    features_2016_discuss_politics=features_2016_discuss_politics,
    features_2016_political_interest=features_2016_political_interest,
    features_2020_attend_church=features_2020_attend_church,
    features_2020_discuss_politics=features_2020_discuss_politics,
    features_2020_political_interest=features_2020_political_interest)
llm_long = redefine_variable(df_list,df_year,'long',features_2012_attend_church=features_2012_attend_church,
    features_2012_discuss_politics=features_2012_discuss_politics,
    features_2012_political_interest=features_2012_political_interest,
    features_2016_attend_church=features_2016_attend_church,
    features_2016_discuss_politics=features_2016_discuss_politics,
    features_2016_political_interest=features_2016_political_interest,
    features_2020_attend_church=features_2020_attend_church,
    features_2020_discuss_politics=features_2020_discuss_politics,
    features_2020_political_interest=features_2020_political_interest)


def dummy_transform(df_list):
    df_year = [2012, 2012, 2012, 2016, 2016, 2016, 2020, 2020, 2020]
    dfs = []
    
    # Validate lengths
    if len(df_list) != len(df_year):
        raise ValueError(f"Length of df_list ({len(df_list)}) must match length of df_year ({len(df_year)})")
    
    for df, year in zip(df_list, df_year):
        if 'race' in df.columns:
            df['race'] = df['race'].replace(6, np.nan)
        if 'abortion_legality' in df.columns:
            df['abortion_legality'] = df['abortion_legality'].replace(5, np.nan)
        if 'bible_truth' in df.columns:
            df['bible_truth'] = df['bible_truth'].replace(5, np.nan)
        if year == 2020:
            if 'race' in df.columns:
                df['race'] = df['race'].map({3:4,4:3}).fillna(df['race'])
            if 'sexual_orientation' in df.columns:
                df['sexual_orientation'] = df['sexual_orientation'].replace(4, np.nan)
            
        if year == 2016:
            if 'gender' in df.columns:
                df['gender'] = df['gender'].replace(3, np.nan)
            if 'family_num' in df.columns:
                df.loc[df['family_num']>= 5, 'family_num'] = 5
            if 'region' in df.columns:
                df.loc[df['region'].isin([9, 10, 23, 25, 33, 34, 36, 42, 44, 50]), 'region'] = 1
                df.loc[df['region'].isin([17, 18, 19, 20, 26, 27, 29, 31, 38, 39, 46, 55]), 'region'] = 2
                df.loc[df['region'].isin([1, 5, 12, 13, 21, 22, 24, 28, 37, 40, 45, 47, 48, 51, 54]), 'region'] = 3
                df.loc[df['region'].isin([2, 4, 6, 8, 15, 16, 30, 32, 35, 41, 49, 53, 56]), 'region'] = 4
            
            df = df.mask(df < 0, pd.NA)
            df = df.dropna()

        else:
            df = df.mask(df < 0, pd.NA)
            df = df.dropna()

        dfs.append(df)
    
    return dfs

llm_long = dummy_transform(llm_long)
llm_short = dummy_transform(llm_short)

llm_long_sampled = []
llm_short_sampled = []

for i in range(len(llm_long)):
    df_long = llm_long[i]
    df_short = llm_short[i]

    target_var = df_long.columns[1]
    class_counts = df_long[target_var].value_counts(normalize=True)
    total_samples = 1000

    sampled_ids = []

    for class_value, proportion in class_counts.items():
        n_samples = int(round(proportion * total_samples))
        class_ids = df_long[df_long[target_var] == class_value]['id'].tolist()
        sampled_class_ids = resample(class_ids, n_samples=n_samples, replace=False, random_state=1998)
        sampled_ids.extend(sampled_class_ids)

    sampled_long = df_long[df_long['id'].isin(sampled_ids)].copy()
    sampled_short = df_short[df_short['id'].isin(sampled_ids)].copy()

    sampled_long = sampled_long.sort_values('id').reset_index(drop=True)
    sampled_short = sampled_short.sort_values('id').reset_index(drop=True)

    llm_long_sampled.append(sampled_long)
    llm_short_sampled.append(sampled_short)







