#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  5 14:31:00 2025

@author: tbj
"""

from common import *

questions_2016 = {
    'V161342': {
        'desc':'gender',
        'vals': {1:'male',2:'female'},
        'question': 'Interviewer: What is your gender? Are you "male" or "female"?',
        },
    'V161310x': {
        'desc':'race',
        'vals': {1:'white',2:'black',3:'asian',5:'hispanic'},
        'question': 'Interviewer: I am going to read you a list of four race categories. What race do you ' + \
                    'consider yourself to be? "White", "Black", "Asian", or "Hispanic"?',
},
    'V161267': {
        'desc':'age',
        'vals': age_map,
        'question': 'Interviewer: What is your age in years?',
        },
    'V161270': {
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
    'V161244': {
        'desc':'church_goer',
        'vals': {1:'yes',2:'no'},
        'question': 'Interviewer: Lots of things come up that keep people from attending religious ' + \
            'services even if they want to. Thinking about your life these days, do you ever' + \
                'attend religious services? Please respond with "yes" or "no".',
},

    'V162125x': {
        'desc':'patriotism',
        'vals': {1:"extremely good", 2:"moderately good", 3:"a little good",
                 4:"neither good nor bad", 5:"a little bad", 6:"moderately bad", 7:"extremely bad"},
        'question': 'Interviewer:  When you see the American flag flying, how does it make you feel? Does ' + \
                    'it make you feel "extremely good", "moderately good", "a little good", "neither good ' + \
                        'nor bad", "a little bad", "moderately bad", or "extremely bad"?'
},
    'V162174': {
        'desc':'discuss_politics',
        'vals': {1:'yes',2:'no'},
        'question': 'Interviewer: Do you ever discuss politics with your family and friends? Please respond ' + \
                    'with "Yes" or "No".'
},
    'V162256': {
        'desc':'political_interest',
        'vals': {1:"very interested", 2:"somewhat interested", 3:"not very interested", 4:"not at all interested"},
        'question': 'Interviewer: How interested would you say you are in politics? Are you "very interested", ' + \
                    '"somewhat interested", "not very interested", or "not at all interested"?',
},
    'V161126': {
        'desc':'ideology',
        'vals': {1:"extremely liberal", 2:"liberal", 3:"slightly liberal",
                 4:"moderate", 5:"slightly conservative", 6:"conservative", 7:"extremely conservative"
                 },
        'question': 'Interviewer: When asked about your political ideology, would you say you are "extremely '+ \
                    'liberal", "liberal", "slightly liberal", "moderate", "slightly conservative", ' + \
                    '"conservative", or "extremely conservative"?',
},
    'V161155': {
        'desc':'pid3',
        'vals': {1:'Democrat',2:'Republican',3:'Independent'},
        'question': 'Interviewer: Generally speaking, do you usually think of yourself as a "Democrat", a ' + \
                '"Republican", or an "Independent"?',
},
    'V161158x': {
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
    'V162031x': {
        'desc':'voted_2016',
        'vals': {0:'no',1:'yes'},
        'question': 'Interviewer: Did you vote in the 2016 general election? Please answer with "yes" or "no".'
        },

    'V162062x': {
        'desc':'votechoice_2016',
        'vals': {1:"Hillary Clinton", 2:"Donald Trump", 3:"Gary Johnson", 4:"Jill Stein", 5:"someone else"},
        'question': 'Interviewer: Which presidential candidate did you vote for in the 2016 presidential ' + \
        'election, "Hillary Clinton", "Donald Trump", "Gary Johnson", "Jill Stein", or "someone else"?',
        },
}