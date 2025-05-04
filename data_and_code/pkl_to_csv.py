#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 06:21:56 2025

@author: tbj
"""
import pandas as pd
import pickle


years = ['2012', '2016', '2020']
engine_name = ['gpt-3.5-turbo','gpt-4o-mini','gpt-4']

#loop over replication datasets by model-year combination
combined_results = {}
for year in years:
    for engine in engine_name:
        filename = f"{year}_{engine}.pkl"
        with open(filename, 'rb') as file:
                    result = pickle.load(file)
        key = f"{year}_{engine}"
        combined_results[key] = result



candidate_mapping = {
    "2012": {"romney": "republican","obama": "democrat"},
    "2016": {"trump": "republican","clinton": "democrat"},
    "2020": {"trump": "republican","biden": "democrat"}
}

#combine all replication data into one dataframe
data = []
for key in combined_results:
    year, engine = key.split("_")
    candidates = candidate_mapping[year]
    republican = list(candidates.keys())[0]
    democrat = list(candidates.keys())[1]
    
    for model_year_result in combined_results[key]:
        caseid = float(model_year_result[0])
        candidate_probs = model_year_result[2][0][0]
        republican_prob = float(candidate_probs[republican])
        democrat_prob = float(candidate_probs[democrat])
        data.append({
            "id": caseid,
            'model': engine,
            "year": year,
            candidates[republican]: republican_prob,
            candidates[democrat]: democrat_prob
        })

replication = pd.DataFrame(data)
replication['year'] = replication['year'].astype(int)


#load authors' davinci output with anes variables
author_data = ['2012 ANES.csv','2016 ANES.csv','2020 ANES.csv']

author_data_list = []
for ad in author_data:
    df = pd.read_csv(ad)
    author_data_list.append(df)

author_2012 = author_data_list[0]
author_2016 = author_data_list[1]
author_2020 = author_data_list[2]

#modify certain columns of the author's data for merging with replication data 
def transform_author_data(df,year_value,model_value = 'gpt-3'):
    columns = list(df.columns)
    columns[0] = 'id'
    columns[1] = 'republican'
    columns[2] = 'democrat'
    columns[3] = 'actual_vote'
    columns[4] = 'race'
    columns[5] = 'discuss_politics'
    columns[6] = 'ideology'
    columns[7] = 'party_id'
    columns[8] = 'church_attendance'
    columns[9] = 'age'
    columns[10] = 'gender'
    columns[11] = 'interest_political_affairs'
    columns[-1] = 'location'
    if str(year_value) in ['2012', '2016']:
        columns[12] = 'patriotism_flag'

    df.columns = columns
    df.insert(loc=1, column='model', value=model_value)
    df.insert(loc=2, column='year', value=year_value)
    if str(year_value) == '2020':
        df.insert(loc=len(df.columns) - 1, column='patriotism_flag', value='NA')
    return df

author_2012 = transform_author_data(author_2012,year_value = 2012)
author_2016 = transform_author_data(author_2016,year_value = 2016)
author_2020 = transform_author_data(author_2020,year_value = 2020)

#concat authors' dataframes
author = pd.concat([author_2012,author_2016,author_2020], axis=0, ignore_index=True)


#merge anes variables to replication
anes_var = author.drop(columns = ['republican','democrat','model'])
replication = pd.merge(replication, anes_var, on=['id', 'year'], how='left')

#concat author and replication
df = pd.concat([author,replication], axis=0, ignore_index=True)
df = df.sort_values(by=['model', 'year'])

df.to_csv('replication_2012_2020.csv', index=False)
