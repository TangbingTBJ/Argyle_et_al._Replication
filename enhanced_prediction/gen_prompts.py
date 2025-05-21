#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 16 03:00:38 2025

@author: tbj
"""

from variable_selection import *

question_and_answer = {
    'race': {
        "template":"Race: XXX",
        "valmap":{ 1:'White.', 2:'Black.', 3:'Asian.', 4:'Native American.', 5:'Hispanic.' },
        },
    'age': {
        "template":"Age: XXX years old.",
        "valmap":{},
        },
    'bible_truth': {
        "template":"Feelings about the Bible: XXX",
        "valmap":{
        1:'The Bible is the actual word of God and is to be taken literally, word for word.',
        2:'The Bible is the word of God but not everything in it should be taken literally.',
        3:'The Bible is a book written by men and is not the word of God.'},
        },
    'attend_church': {
        "template":"Religious service attendance: XXX",
        "valmap":{
        1:'Yes.',
        2:'No.'},
        },
    'abortion_legality': {
        "template":"Opinion on abortion: XXX",
        "valmap":{
        1:'By law, abortion should never be permitted.',
        2:"By law, abortion should be permitted only in case of rape, incest, or when the woman's life in danger.",
        3:"By law, abortion should be permitted for reasons other than rape, incest, or when the woman's life in danger.",
        4:"By law, abortion should be permitted as a matter of personal choice."},
        },
    'ideology': {
        "template":"Party identification: XXX",
        "valmap":{
        1:'Strong Democrat.',
        2:"Not very strong Democrat.",
        3:"Independent but lean Democrat.",
        4:"Independent.",
        5:"Independent but lean Republican.",
        6:"Not very strong Republican.",
        7:"Strong Republican."},
        },
    'family_num': {
        "template":"Number of cohabiting family members: XXX",
        "valmap":{
        0:'Zero.',
        1:'One.',
        2:"Two.",
        3:"Three.",
        4:"Four.",
        5:"Five or more."},
        },
    'life_satisfaction': {
        "template":"Satisfaction with life: XXX",
        "valmap":{
        1:'Extremely satisfied.',
        2:"Very satisfied.",
        3:"Moderately satisfied.",
        4:"Slightly satisfied.",
        5:"Not satisfied at all."},
        },
    'health': {
        "template":"Health status: XXX",
        "valmap":{
        1:'Excellent.',
        2:"Very good.",
        3:"Good.",
        4:"Fair.",
        5:"Poor."},
        },
    'political_interest': {
        "template":"Interest in politics: XXX",
        "valmap":{
        1:'Very interested.',
        2:"Somewhat interested.",
        3:"Not very interested.",
        4:"Not at all interested."},
        },
    'trust': {
        "template":"Tendency to trust in others: XXX",
        "valmap":{
        1:'Always.',
        2:"Most of the time.",
        3:"About half the time.",
        4:"Some of the time.",
        5:"Never."},
        },
    'election_impact': {
        "template":"Effectiveness of election at holding governments accountable to public opinion: XXX",
        "valmap":{
        1:'A good deal.',
        2:"Some.",
        3:"Not much."},
        },
    'voting_duty': {
        "template":"Voting as duty or choice: XXX",
        "valmap":{
        1:'Very strongly a duty.',
        2:"Moderately strongly a duty.",
        3:"A little strongly a duty.",
        4:"Neither a duty nor a choice.",
        5:"A little strongly a choice.",
        6:"Moderately strongly a choice.",
        7:"Very strongly a choice."},
        },
    'immigration_policy': {
        "template":"Attitude toward unauthorized immigrants: XXX",
        "valmap":{
        1:'Make all unauthorized immigrants felons and send them back to their home country.',
        2:"Have a guest worker program that allows unauthorized immigrants to remain in the US.",
        3:"Allow unauthorized immigrants to remain in the US & eventually qualify for citizenship but only if they meet requirements.",
        4:"Allow unauthorized immigrants to remain in the US & eventually qualify for citizenship without penalties."},
        },
    'finance_next': {
        "template":"Relative to the current financial situation, the future situation will be: XXX",
        "valmap":{
        1:'Much better.',
        2:"Somewhat better.",
        3:"About the same.",
        4:"Somewhat worse.",
        5:"Much worse."},
        },
    'finance_past': {
        "template":"Relative to the current financial situation, the past situation was: XXX",
        "valmap":{
        1:'Much better.',
        2:"Somewhat better.",
        3:"About the same.",
        4:"Somewhat worse.",
        5:"Much worse."},
        },
    'environment_protection': {
        "template":"Level of federal spending on environmental protection: XXX",
        "valmap":{
        1:'Should be increased.',
        2:"Should be decreased.",
        3:"Should be kept the same."},
        },
    'campaign_interest': {
        "template":"Interest in political campaigns: XXX",
        "valmap":{
        1:'Very much interested.',
        2:"Somewhat interested.",
        3:"Not much interested."},
        },
    'welfare_spend': {
        "template":"Level of federal spending on welfare programs: XXX",
        "valmap":{
        1:'Should be increased.',
        2:"Should be decreased.",
        3:"Should be kept the same."},
        },
    'gun_control': {
        "template":"Laws on gun acquisition: XXX",
        "valmap":{
        1:'Should be made more stringent.',
        2:"Should be made less stringent.",
        3:"Should be kept the same."},
        },
    'discuss_politics': {
        "template":"Discusses politics with family and friends: XXX",
        "valmap":{
        1:'Yes.',
        2:"No."},
        },
    'gender': {
        "template":"Gender: XXX",
        "valmap":{
        1:'Male.',
        2:"Female."},
        },
    'region': {
        "template":"Physical location: XXX",
        "valmap":{
        1:'U.S. Northeast.',
        2:"U.S. Midwest.",
        3:"U.S. South.",
        4:"U.S. West."},
        },
    'congress_approval': {
        "template":"Congressional job approval: XXX",
        "valmap":{
        1:'Approve.',
        2:"Disapprove."},
        },
    }

qna_keys = question_and_answer.keys()



def gen_qa_per_df(df_list):
    years = [2012, 2016, 2020]
    target_vars = ['attend_church', 'discuss_politics', 'political_interest']
    results = {}
    
    index_mapping = {}
    idx = 0
    for year in years:
        for target_var in target_vars:
            index_mapping[idx] = (target_var, year)
            idx += 1
    
    for i, df in enumerate(df_list):
        qa_list = []
        if i not in index_mapping:
            continue
        
        target_variable, year = index_mapping[i]
        
        for row_idx, (_, row) in enumerate(df.iterrows()):
            qa = "Examine the individual's survey responses carefully:"
            for q in qna_keys:
                if q in df.columns and q != target_variable:
                    anes_value = row[q]
                    template = question_and_answer[q]['template']
                    valmap = question_and_answer[q]['valmap']
                    if pd.isna(anes_value):
                        qa += f" {template.replace('XXX', '[MISSING]')}"
                    else:
                        qa += f" {template.replace('XXX', valmap.get(anes_value, str(anes_value)))}"
            
            target_template = question_and_answer[target_variable]['template']
            target_valmap = question_and_answer[target_variable]['valmap']
            choices = '; '.join([f"{k}: {v}" for k, v in target_valmap.items()])
            qa += f" {target_template.replace('XXX', '[Based on the above characteristics, predict the most likely choice and respond with only the corresponding number (e.g., 1, 2, 3, 4). Do not include any text, punctuation, or explanation.]')} Possible choices: {choices}"
            qa_list.append(qa)
        
        results[f"{target_variable}_{year}"] = qa_list
    
    return results

# generate prompts
llm_short_for_gpt = gen_qa_per_df(llm_short_sampled)
llm_long_for_gpt = gen_qa_per_df(llm_long_sampled)



