#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  5 14:51:44 2025

@author: tbj
"""

from common import *

questions_2020 = {
    'V201600': {
        'desc':'gender',
        'vals': {1:'male',2:'female'},
        'question': 'Interviewer: What is your gender? Are you "male" or "female"?',
        },
    'V201549x': {
        'desc':'race',
        'vals': {1:'white',2:'black',3:'hispanic',4:'asian'},
        'question': 'Interviewer: I am going to read you a list of four race categories. What race do you ' + \
                    'consider yourself to be? "White", "Black", "Hispanic", or "Asian"?',
},
    'V201507x': {
        'desc':'age',
        'vals': age_map,
        'question': 'Interviewer: What is your age in years?',
        },
    'V201510': {
        'desc':'education',
        'vals': {
            1:'high school',
            2:'high school',
            3:'some college',
            4:'some college',
            5:'some college',
            6:'a four-year college degree',
            7:'an advanced degree',
            8:'an advanced degree',
        },
        'question': 'Interviewer: What is the highest level of school you have completed, or the highest ' + \
                    'degree you have received? Is it "high school", "some college", "a four-year college ' + \
                    'degree", or "an advanced degree"?',
},
    'V201452': {
        'desc':'church_goer',
        'vals': {1:'yes',2:'no'},
        'question': 'Interviewer: Lots of things come up that keep people from attending religious ' + \
            'services even if they want to. Thinking about your life these days, do you ever' + \
                'attend religious services? Please respond with "yes" or "no".',
},

    'V202022': {
        'desc':'discuss_politics',
        'vals': {1:'yes',2:'no'},
        'question': 'Interviewer: Do you ever discuss politics with your family and friends? Please respond ' + \
                    'with "Yes" or "No".'
},
    'V202406': {
        'desc':'political_interest',
        'vals': {1:"very interested", 2:"somewhat interested", 3:"not very interested", 4:"not at all interested"},
        'question': 'Interviewer: How interested would you say you are in politics? Are you "very interested", ' + \
                    '"somewhat interested", "not very interested", or "not at all interested"?',
},
    'V201200': {
        'desc':'ideology',
        'vals': {1:"extremely liberal", 2:"liberal", 3:"slightly liberal",
                 4:"moderate", 5:"slightly conservative", 6:"conservative", 7:"extremely conservative"
                 },
        'question': 'Interviewer: When asked about your political ideology, would you say you are "extremely '+ \
                    'liberal", "liberal", "slightly liberal", "moderate", "slightly conservative", ' + \
                    '"conservative", or "extremely conservative"?',
},
    'V201228': {
        'desc':'pid3',
        'vals': {1:'Democrat',2:'Republican',3:'Independent'},
        'question': 'Interviewer: Generally speaking, do you usually think of yourself as a "Democrat", a ' + \
                '"Republican", or an "Independent"?',
},
    'V201231x': {
        'desc':'pid7',
        'vals': {1:"strong democrat", 2:"not very strong democrat",
                 3:"independent, but closer to the Democratic party", 4:"independent",
                 5:"independent, but closer to the Republican party", 6:"not very strong Republican",
                 7:"strong Republican"},
        'question': 'Interviewer: Which would you say best describes your partisan identification. ' + \
                    'Would you say you are a "strong democrat", "not very strong democrat", ' + \
                        '"independent, but closer to the Democratic party", "independent", "independent, ' + \
                            'but closer to the Republican party", "not very strong Republican", or "strong Republican"?',
},
    'V202072': {
        'desc':'voted_2020',
        'vals': {2:'no',1:'yes'},
        'question': 'Interviewer: Did you vote in the 2020 general election? Please answer with "yes" or "no".'
        },

    'V202110x': {
        'desc':'votechoice_2020',
        'vals': {1:"Joe Biden", 2:"Donald Trump", 3:"Jo Jorgensen", 4:"Howie Hawkins", 5:"someone else"},
        'question': 'Interviewer: Which presidential candidate did you vote for in the 2020 presidential ' + \
        'election, "Joe Biden, "Donald Trump", "Jo Jorgensen", "Howie Hawkins", or "someone else"?',
        },
}