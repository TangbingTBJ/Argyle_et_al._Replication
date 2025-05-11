#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  5 13:41:10 2025

@author: tbj
"""

from common import *

questions_2012 = {
    'gender_respondent_x': {
        'desc':'gender',
        'vals': {1:'male',2:'female'},
        'question': 'Interviewer: What is your gender? Are you "male" or "female"?',
        },
    'dem_raceeth_x': {
        'desc':'race',
        'vals': {1:'white',2:'black',3:'asian',5:'hispanic'},
        'question': 'Interviewer: I am going to read you a list of four race categories. What race do you ' + \
                    'consider yourself to be? "White", "Black", "Asian", or "Hispanic"?',
},
    'dem_age_r_x': {
        'desc':'age',
        'vals': age_map,
        'question': 'Interviewer: What is your age in years?',
        },
    'dem_edu': {
        'desc':'education',
        'vals': {
            1:'high school',
            2:'high school',
            3:'high school',
            4:'high school',
            5:'high school',
            6:'high school',
            7:'high school',
            8:'high school',
            9:'high school',
            10:'some college',
            11:'some college',
            12:'some college',
            13:'a four-year college degree',
            14:'an advanced degree',
            15:'an advanced degree',
            16:'an advanced degree',
        },
        'question': 'Interviewer: What is the highest level of school you have completed, or the highest ' + \
                    'degree you have received? Is it "high school", "some college", "a four-year college ' + \
                    'degree", or "an advanced degree"?',
},
    'relig_church': {
        'desc':'church_goer',
        'vals': {1:'yes',2:'no'},
        'question': 'Interviewer: Lots of things come up that keep people from attending religious ' + \
            'services even if they want to. Thinking about your life these days, do you ever' + \
                'attend religious services? Please respond with "yes" or "no".',
},

    'patriot_flag': {
        'desc':'patriotism',
        'vals': {1:"extremely good", 2:"very good", 3:"moderately good",
                 4:"slightly good", 5:"not good at all"},
        'question': 'Interviewer:  When you see the American flag flying, how does it make you feel? Does ' + \
                    'it make you feel "extremely good", "very good", "moderately good", "slightly good" '+ \
                    '"not good at all"?'
},
    'discuss_disc': {
        'desc':'discuss_politics',
        'vals': {1:'yes',2:'no'},
        'question': 'Interviewer: Do you ever discuss politics with your family and friends? Please respond ' + \
                    'with "Yes" or "No".'
},
    'paprofile_interestpolit': {
        'desc':'political_interest',
        'vals': {1:"very interested", 2:"somewhat interested", 3:"slightly interested", 4:"not at all interested"},
        'question': 'Interviewer: How interested would you say you are in politics? Are you "very interested", ' + \
                    '"somewhat interested", "slightly interested", or "not at all interested"?',
},
    'libcpre_self': {
        'desc':'ideology',
        'vals': {1:"extremely liberal", 2:"liberal", 3:"slightly liberal",
                 4:"moderate", 5:"slightly conservative", 6:"conservative", 7:"extremely conservative"
                 },
        'question': 'Interviewer: When asked about your political ideology, would you say you are "extremely '+ \
                    'liberal", "liberal", "slightly liberal", "moderate", "slightly conservative", ' + \
                    '"conservative", or "extremely conservative"?',
},
    'pid_self': {
        'desc':'pid3',
        'vals': {1:'Democrat',2:'Republican',3:'Independent'},
        'question': 'Interviewer: Generally speaking, do you usually think of yourself as a "Democrat", a ' + \
                '"Republican", or an "Independent"?',
},
    'pid_x': {
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
    'rvote2012_x': {
        'desc':'voted_2012',
        'vals': {2:'no',1:'yes'},
        'question': 'Interviewer: Did you vote in the 2012 general election? Please answer with "yes" or "no".'
        },

    'presvote2012_x': {
        'desc':'votechoice_2012',
        'vals': {1:"Barack Obama", 2:"Mitt Romney", 5:"someone else"},
        'question': 'Interviewer: Which presidential candidate did you vote for in the 2012 presidential ' + \
        'election, "Barack Obama", "Mitt Romney", or "someone else"?',
        },
}