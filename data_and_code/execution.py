#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 27 03:23:42 2025

@author: tbj
"""
import sys

sys.argv = ['your_script.py', '2012'] #2012 2016 2020
engine_name = 'gpt-4'  #'gpt-3.5-turbo','gpt-4o-mini','gpt-4'

import pandas as pd
import pickle
from tqdm import tqdm
# for cost analysis
from transformers import GPT2Tokenizer

if sys.argv[1] == '2012':
    from anes2012 import *
if sys.argv[1] == '2016':
    from anes2016 import *
if sys.argv[1] == '2020':
    from anes2020 import *
from common import *

foi_keys = fields_of_interest.keys()

if sys.argv[1] == '2012':
    if engine_name == 'gpt-4o-mini' or engine_name == 'gpt-4':
        query = "In the 2012 presidential election, Mitt Romney is the Republican candidate, "
        query += "and Barack Obama is the Democratic candidate. Answering only with the candidate's name, I voted for"
    else:
        query = "In the 2012 presidential election, I voted for"
        
if sys.argv[1] == '2016':
    if engine_name == 'gpt-4o-mini' or engine_name == 'gpt-4':
        query = "In the 2016 presidential election, Donald Trump is the Republican candidate, "
        query += "and Hillary Clinton is the Democratic candidate. Answering only with the candidate's name, I voted for"
    else:
        query = "In the 2016 presidential election, I voted for"
        
if sys.argv[1] == '2020':
    if engine_name == 'gpt-4o-mini' or engine_name == 'gpt-4':
        query = "In the 2020 presidential election, Donald Trump is the Republican candidate, "
        query += "and Joe Biden is the Democratic candidate. Answering only with the candidate's name, I voted for"
    else:
        query = "In the 2020 presidential election, Donald Trump is the Republican candidate, "
        query += "and Joe Biden is the Democratic candidate, and I voted for"
    
# ============================================================================================
#
'''
def cost_approximation(prompt, engine="davinci", tokenizer=None):
    possible_engines = ["davinci", "curie", "babbage", "ada"]
    assert engine in possible_engines, f"{engine} is not a valid engine"
    if tokenizer==None:
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    num_tokens = len(tokenizer(prompt)['input_ids'])
    if engine == "davinci":
        cost = (num_tokens / 1000) * 0.0600    #0.02
    elif engine == "curie":
        cost = (num_tokens / 1000) * 0.0060    #0.002
    elif engine == "babbage":
        cost = (num_tokens / 1000) * 0.0012    #0.0005
    else:
        cost = (num_tokens / 1000) * 0.0008    #0.0004
    return cost, num_tokens
'''

def gen_backstory(pid, df):
    person = df.iloc[pid]
    backstory = ""
    for k in foi_keys:
        anes_val = person[k]     #respondent's value for characteristic k 
        elem_template = fields_of_interest[k]['template']    #temporary template for characteristic k
        elem_map = fields_of_interest[k]['valmap']     #value mapping for characteristic k
        if len(elem_map) == 0:   #for age 
            backstory += " " + elem_template.replace('XXX', str(anes_val))
        elif anes_val in elem_map:
            backstory += " " + elem_template.replace('XXX', elem_map[anes_val])
    if backstory[0] == ' ':
        backstory = backstory[1:]
    return backstory


#
# ============================================================================================
# ============================================================================================
#

#anesdf = pd.read_csv( ANES_FN, sep=SEP, encoding='latin-1' )
anesdf = pd.read_csv(ANES_FN)
#anesdf = anesdf[0:30]
#costs = []
#numtoks = []
#tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

full_results = []
for pid in tqdm( range(len(anesdf)) ):
    if "V200003" in anesdf.iloc[pid] and anesdf.iloc[pid]["V200003"]==2: print( f"SKIPPING {pid}..." )
    # we want to exclude cases marked as 2 on this variable;
    # those are the panel respondents (interviewed in 2016 and 2020) continue
    anes_id = anesdf.iloc[pid][ID_COL]    #extract respondent id 
    prompt = gen_backstory( pid, anesdf )
    prompt += " " + query #print("---------------------------------------------------") base query in anes.py
    #print( prompt )
    #cost, numtok = cost_approximation( prompt, engine="davinci", tokenizer=tokenizer )
    #costs.append( cost )
    #numtoks.append( numtok )
    results = run_prompts( [prompt], tok_sets, engine= engine_name ) #print(results[0][0])
    full_results.append( (anes_id, prompt, results) )
   # full_results.append(prompt)   #for testing prompt only 

def output_name (date,engine_name):
    OUTPUT_FN = f"./{date}_{engine_name}.pkl"
    return OUTPUT_FN
OUTPUT_FN = output_name(sys.argv[1], engine_name)

#print( "Total cost: ", np.sum(np.array(costs)) )
#print( "Averge numtok: ", np.mean(np.array(numtoks)) )
pickle.dump( full_results, open(OUTPUT_FN,"wb") )



#print(type(anesdf))
#print(anesdf.shape)
#print(anesdf.head())













