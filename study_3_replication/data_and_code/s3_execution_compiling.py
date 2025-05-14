import sys
import numpy as np
import openai
import time
import pandas as pd
import pickle
from tqdm import tqdm
import os
import concurrent.futures
from common import *

openai.api_key = ""

def render_question(s, q, last_q=False):
    txt = ''
    if sys.argv[1] == '2012': 
        questions = questions_2012
        party_id = 'pid_self'
        close_r_d = 'pid_strong'
        no_party = 'pid_lean'
    elif sys.argv[1] == '2016':
        questions = questions_2016
        party_id = 'V161155'
        close_r_d = 'V161156'
        no_party = 'V161157'
    elif sys.argv[1] == '2020':
        questions = questions_2020
        party_id = 'V201228'
        close_r_d = 'V201229'
        no_party = 'V201230'
   #question code   
    if q == party_id:
        #row[question code]  if respondent's answer is in question 
        if s[q] in questions[q]['vals']:
            txt += questions[q]['question'] + "\n"
            if last_q:
                return txt
            txt += f"Me: {questions[q]['vals'][s[q]]}\n\n"

        if s[party_id] == 2 and s[close_r_d] > 0:
            txt += 'Interviewer: Thinking about your identification with the Republican party, would you say ' + \
                'it is "strong" or a "not very strong"?\n'
            if last_q:
                txt += f"Me:"
                return txt
            if s[close_r_d] == 1:
                txt += f"Me: strong\n\n"
            elif s[close_r_d] == 2:
                txt += f"Me: not very strong\n\n"
                
        if s[party_id] == 1 and s[close_r_d] > 0:
            txt += 'Interviewer: Thinking about your identification with the Democratic party, would you say ' + \
               'it is "strong" or a "not very strong"?\n'
            if last_q:
                txt += f"Me:"
                return txt
            if s[close_r_d] == 1:
                txt += f"Me: strong\n\n"
            elif s[close_r_d] == 2:
                txt += f"Me: not very strong\n\n"

        if s[party_id] == 3 and s[no_party] > 0:
            txt += 'Interviewer: Do you think of yourself as "closer to the Republican Party", "closer to the ' + \
                   'Democratic party", or "closer to neither party"?\n'
            if last_q:
                txt += f"Me:"
                return txt
            if s[no_party] == 1:
                txt += "Me: closer to the Republican Party\n\n"
            elif s[no_party] == 2:
                txt += "Me: closer to neither party\n\n"
            elif s[no_party] == 3:
                txt += "Me: closer to the Democratic party\n\n"
        return txt

    if last_q:
        txt += questions[q]['question'] + "\n"
        txt += f"Me:"
        return txt
    if s[q] in questions[q]['vals']:
        txt += questions[q]['question'] + "\n"
        txt += f"Me: {questions[q]['vals'][s[q]]}\n\n"
        return txt
    else:
        return txt

#maps human-readable question identifier  to its ANES question code
def find_q(questions, hrq):
    for q in questions.keys():
        if questions[q]['desc'] == hrq:
            return q


def build_interview(s, human_readable_omit=None):
    txt = ''
    if sys.argv[1] == '2012': 
        questions = questions_2012
        human_readable_question_order = ['gender', 'race', 'age', 'education', 'church_goer',
                                         'patriotism', 'discuss_politics', 'political_interest', 'ideology', 
                                         'pid3','pid7','voted_2012', 'votechoice_2012']
    if sys.argv[1] == '2016': 
        questions = questions_2016
        human_readable_question_order = ['gender', 'race', 'age', 'education', 'church_goer',
                                         'patriotism', 'discuss_politics', 'political_interest', 'ideology',
                                         'pid3','pid7','voted_2016', 'votechoice_2016']
    if sys.argv[1] == '2020': 
        questions = questions_2020
        human_readable_question_order = ['gender', 'race', 'age', 'education', 'church_goer',
                                         'discuss_politics', 'political_interest', 'ideology',
                                         'pid3','pid7','voted_2020', 'votechoice_2020']
    omit = None
    if human_readable_omit:
        omit = find_q( questions, human_readable_omit)  #find the question code of omitted question 
    for hrq in human_readable_question_order:
        q = find_q( questions, hrq )
        if q == omit:     #if the current question code q matches the omitted question code 
            continue
        if hrq=='votechoice_2012' and s['rvote2012_x'] == 2:
            continue
        if hrq=='votechoice_2016' and s['V162031x'] == 0:
            continue
        if hrq=='votechoice_2020' and s['V202072'] == 0:
            continue
        txt += render_question( s, q, last_q=False )
    if human_readable_omit:                           #loops over all the non-omitted questions first, then call render question again to make the omitted one
        txt += render_question( s, omit, last_q=True )
        return txt
    

def strcompare(s1, s2):
    s1 = s1.lower().strip()
    s2 = s2.lower().strip()
    return s1.startswith(s2) or s2.startswith(s1)

                 #row index
def process_row(row, ind, hr_omit, engine_name, questions, omit, year, id_col):
        id_val = row[id_col]
        sys.argv = ['script.py', year]  
        prompt = build_interview(row, human_readable_omit=hr_omit)
        
        full_results = do_query(prompt, engine=engine_name, max_tokens=5, temperature=0.7)
        
        original_response = full_results[1].choices[0].message.content
        samp_response = original_response.strip().removeprefix("Me:").strip()
        coded_response = -1
        for valnum in questions[omit]['vals'].keys():
            if questions[omit]['vals'][valnum] in samp_response or strcompare(questions[omit]['vals'][valnum], samp_response):
                coded_response = valnum
        
        return {
            "id": id_val,
            "hr_omit": hr_omit,
            "prompt": prompt,
            "original_response": original_response,
            "sampled_response": samp_response,
            "coded_response": coded_response,
            "full_results": full_results
        }


if __name__ == "__main__":
    from s3_anes2012 import questions_2012
    from s3_anes2016 import questions_2016
    from s3_anes2020 import questions_2020

    #year = sys.argv[1]
    year = '2016'
    engine_name = 'gpt-3.5-turbo'   #'gpt-3.5-turbo','gpt-4o-mini','gpt-4'
    hr_omits = ['political_interest', 'church_goer', 'discuss_politics']
    
    # configure data based on year
    data_configs = {
        '2012': {'file': 'study_3_anes_2012.csv', 'questions': questions_2012, 'id_col': 'caseid'},
        '2016': {'file': 'study_3_anes_2016.csv', 'questions': questions_2016, 'id_col': 'V160001'},
        '2020': {'file': 'study_3_anes_2020.csv', 'questions': questions_2020, 'id_col': 'V200001'}
    }
    
    config = data_configs[year]
    df = pd.read_csv(config['file'])
    questions = config['questions']
    id_col = config['id_col']
    
    for hr_omit in hr_omits:
        omit = find_q(questions, hr_omit)
        
        final_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_row, row, ind, hr_omit, engine_name, questions, omit, year, id_col) for ind, row in df.iterrows()]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc=f"Processing {hr_omit}"):
                result = future.result()
                if result is not None:
                    final_results.append(result)
        
        # Save results
        output_prefix = f"{hr_omit}_{engine_name}_{year}"
        with open(f"{output_prefix}_results.csv", "w") as fout:
            keys = [id_col] + list(questions.keys())
            print(",".join(keys) + ",gpt_coded_response", file=fout)
            for i, row in enumerate(tqdm(df.itertuples(), total=len(df), desc=f"Saving {output_prefix}")):
                matching_result = next((r for r in final_results if r['id'] == getattr(row, id_col)), None)
                if matching_result:
                    values = [str(getattr(row, k) if k != id_col else str(getattr(row, id_col))) for k in keys]
                    print(",".join(values) + f",{matching_result['coded_response']}", file=fout)
        
        pickle.dump(final_results, open(f"{output_prefix}_full_results.pkl", "wb"))



'''
if __name__ == "__main__":
    from s3_anes2012 import questions_2012
    from s3_anes2016 import questions_2016
    from s3_anes2020 import questions_2020

    #year = sys.argv[1]
    year = '2020'
    engine_name = 'gpt-3.5-turbo'   #'gpt-3.5-turbo','gpt-4o-mini','gpt-4'
    hr_omits = ['political_interest', 'church_goer', 'discuss_politics']
    
    # configure data based on year
    data_configs = {
        '2012': {'file': 'study_3_anes_2012.csv', 'rows': 10, 'questions': questions_2012, 'id_col': 'caseid'},
        '2016': {'file': 'study_3_anes_2016.csv', 'rows': 10, 'questions': questions_2016, 'id_col': 'V160001'},
        '2020': {'file': 'study_3_anes_2020.csv', 'rows': 10, 'questions': questions_2020, 'id_col': 'V200001'}
    }
    
    config = data_configs[year]
    df = pd.read_csv(config['file'])[:config['rows']]
    questions = config['questions']
    id_col = config['id_col']
    
    for hr_omit in hr_omits:
        omit = find_q(questions, hr_omit)
        
        final_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_row, row, ind, hr_omit, engine_name, questions, omit, year, id_col) for ind, row in df.iterrows()]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc=f"Processing {hr_omit}"):
                result = future.result()
                if result is not None:
                    final_results.append(result)
        
        # Save results
        output_prefix = f"{hr_omit}_{engine_name}_{year}"
        with open(f"{output_prefix}_results.csv", "w") as fout:
            keys = [id_col] + list(questions.keys())
            print(",".join(keys) + ",gpt_coded_response", file=fout)
            for i, row in enumerate(tqdm(df.itertuples(), total=len(df), desc=f"Saving {output_prefix}")):
                matching_result = next((r for r in final_results if r['id'] == getattr(row, id_col)), None)
                if matching_result:
                    values = [str(getattr(row, k) if k != id_col else str(getattr(row, id_col))) for k in keys]
                    print(",".join(values) + f",{matching_result['coded_response']}", file=fout)
        
        pickle.dump(final_results, open(f"{output_prefix}_full_results.pkl", "wb"))
'''
        
       

with open('discuss_politics_gpt-3.5-turbo_2016_full_results.pkl', 'rb') as f:
    check = pickle.load(f)
        
        
        