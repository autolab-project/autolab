# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 19:24:07 2019

@author: qchat
"""

from threading import Thread

import uuid
session = uuid.uuid4().hex

def startup() :

    StatisticsThread('startup').start()


class StatisticsThread(Thread) :
    
    def __init__(self,action) :
        Thread.__init__(self)
        self.action = action
        
    def run(self):
        
        import requests
        
        data = {
            'v': '1',  # API Version.
            't': 'event',  # Event hit type.
            'tid': 'UA-152731770-2',  # Tracking ID / Property ID of the Google Analytics property
            'cid': session, # Random Unique Anonymous Client Identifier (NOT BASED AT ALL ON THE DEVICE)
            'ec': 'package',  # Event category.
            'ea': self.action  # Event action.
        }
        
        try : requests.post('https://ssl.google-analytics.com/collect', data=data)
        except : pass
        