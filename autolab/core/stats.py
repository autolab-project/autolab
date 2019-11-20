# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 19:24:07 2019

@author: qchat
"""

from threading import Thread
import autolab

def startup() :
    
    ''' Send a 'startup' anonymous event to google analytics '''

    send('startup')
    
    
    
def send(action):
    
    ''' Send a <action> anonymous event to google analytics '''
    
    if is_stats_enabled():
        StatisticsThread(action).start()
        
        
        
def set_stats_enabled(state):
    
    """ This function enable or disable the anonymous statistics feature of Autolab """
    
    assert isinstance(state,bool), "The state has to be a boolean."
    autolab._config.set_value('stats','enabled',str(int(state)))
    
    
    
def is_stats_enabled():
    
    """ This function the activation state of the anonymous statistics feature of Autolab """
    
    return autolab._config.get_value('stats','enabled') == '1' 


def get_explanation():
    
    return '''At startup, Autolab is configured to send only once a completely anonymous signal (sha256 hashed ID) over internet for statistics of use. This helps the authors to have a better understanding of how the package is used worldwide. No personal data is transmitted during this process. Also, this is done in background, with no impact on the performance of Autolab.'''
class StatisticsThread(Thread) :
    
    def __init__(self,action) :
        Thread.__init__(self)
        self.action = action
        
    def run(self):
        
        ''' Send an anonymous event to google analytics '''
        
        import requests
        import hashlib
        import uuid
        import socket
        
        # Fabrication of a unique anonymous identifier based on the hostname and mac address
        uid = socket.gethostname()+hex(uuid.getnode())
        uid = hashlib.sha256(uid.encode()).hexdigest()   

        # Preparing payload
        data = {
            'v': '1',  # API Version.
            't': 'event',  # Event hit type.
            'tid': 'UA-152731770-3',  # Tracking ID / Property ID of the Google Analytics property
            'cid': uid, # Unique Anonymous Client Identifier
            'ec': 'package',  # Event category.
            'ea': self.action,  # Event action.
            'el': autolab.__version__ # Event label
        }
        
        try : 
            requests.post('https://www.google-analytics.com/collect', data=data)
        except : pass
        