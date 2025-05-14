#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 26 19:14:55 2025

@author: tbj
"""
import openai
import numpy as np
import time
import logging
openai.api_key = ''"


def logsumexp( log_probs ):
    log_probs = log_probs - np.max(log_probs)
    log_probs = np.exp(log_probs)
    log_probs = log_probs / np.sum( log_probs )
    return log_probs

def extract_probs( lp ):
    lp_keys = list( lp.keys() ) #lp: {"Donald": -0.5, "Hillary": -1.2}
    ps = [ lp[k] for k in lp_keys ]  #[-0.5, -1.2]
    ps = logsumexp( np.asarray(ps) ) #[0.731, 0.269]
    vals = [ (lp_keys[ind], ps[ind]) for ind in range(len(lp_keys)) ]  #[("Donald", 0.731), ("Hillary", 0.269)]
    vals = sorted( vals, key=lambda x: x[1], reverse=True ) #reverse sort on probability
    result = {}
    for v in vals: #v = tuple element
        result[ v[0] ] = v[1] #dict assign 1st element as key and 2nd as value
    return result

'''
def do_query( prompt, max_tokens=2, engine="davinci" ):
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=0.7,
        max_tokens=max_tokens,
        top_p=1,
        logprobs=100, #log-probabilities for the top 100 tokens at each position, a dictionary of the top 100 possible tokens and their log-probabilities
    )
    token_responses = response['choices'][0]['logprobs']['top_logprobs']       #response['choices'][0]: output for the entire completion token    #{' Donald': -0.5, ' Hillary': -1.2, ' Bernie': -2.0, ...},  # Position 0 (first token) {' Trump': -0.8, ' Clinton': -1.5, ' Sanders': -2.5, ...}
    results = []
    for ind in range(len(token_responses)): 
        results.append( extract_probs( token_responses[ind] ) )  #[{" Donald": 0.731, " Hillary": 0.269, " Bernie": 0.0001}, {" Trump": 0.692, " Clinton": 0.308, " Sanders": 0.0001}]
    return results, response

'''

def do_query( prompt, engine,temperature,max_tokens ):
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    try:
        #logging.basicConfig(level=logging.DEBUG)
        response = openai.chat.completions.create(
            model=engine,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            logprobs=True,
            top_logprobs=20
        )
    except openai.BadRequestError as e:
        print(f"BadRequestError: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    
    token_responses = []
    for choice in response.choices:
        if choice.logprobs:
            for token_logprob in choice.logprobs.content:
                top_logprobs = {item.token: item.logprob for item in token_logprob.top_logprobs}
                token_responses.append(top_logprobs)
    
    return token_responses, response


def collapse_r( response, toks ):
    total_prob = 0.0
    for t in toks:
        if t in response:
            total_prob += response[t]
    return total_prob

def print_response( template_val, tok_sets, response ): #print( f"{template_val}" )
    print( tok_sets )
    tr = []
    for tok_set_key in tok_sets.keys():
        toks = tok_sets[tok_set_key] #all the possible tokens associated with the candidate
        full_prob = collapse_r( response[0], toks ) 
        tr.append( full_prob )
        #print( f";{tok_set_key};{full_prob}", end="" ) #print( "\t{:.2f}".format(full_prob), end="" )
        print("\t\t",end="")
    tr = np.asarray( tr )
    tr = tr / np.sum(tr)
    for ind, tok_set_key in enumerate( tok_sets.keys() ): #for index and key
        print( f"\t{tok_set_key}\t{tr[ind]}", end="" )
        #print( "\t{:.2f}".format(tr[ind]), end="" )
print("")

def parse_response( template_val, tok_sets, response ):
    tr = []
    for tok_set_key in tok_sets.keys():
        toks = tok_sets[tok_set_key]
        full_prob = collapse_r( response[0], toks )
        tr.append( full_prob )
    tr = np.asarray( tr )
    tr = tr / np.sum(tr)
    results = {}
    for ind, tok_set_key in enumerate( tok_sets.keys() ):
        results[ tok_set_key ] = tr[ind] #append back candidate with their normalized probability
    return results #{ "Trump": 0.6316, "Clinton": 0.3158}

def run_prompts( prompts, tok_sets, engine ):
    results = []
    for prompt in prompts: #print("---------------------------------------------------")
#print( prompt )
        response, full_response = do_query( prompt, engine, max_tokens = 2 ) #print( response )
#print_response( prompt, tok_sets, response )
        simp_results = parse_response( prompt, tok_sets, response )
#print( simp_results )
        time.sleep( 0.1 )
        results.append( (simp_results, response, full_response) )
    return results

def run_experiment( template, template_vals, tok_sets ):
    prompts = []
    for template_val in template_vals:
        grounded_prompt = template.replace( "XXX", template_val )
        prompts.append( grounded_prompt )
    return run_prompts( prompts, tok_sets )

age_map = {}
for ind in range(100):
    age_map[ind]=str(ind)






