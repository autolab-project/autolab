# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 15:38:44 2020

@author: qchat
"""

from threading import Thread
from . import config
from .. import __version__

init_text = '''[AUTOLAB Telemetry - first launch]\nFor statistics of use, Autolab will try to send signals over internet to help its authors to have a better understanding of how the package is used worldwide. No personal data is transmitted (anonymous sha256 hashed UID). Also, this is done in background, with no impact on the performance.'''

def startup() :

    ''' Send a 'startup' anonymous event to google analytics '''

    send('startup')



def send(action):

    ''' Send a <action> anonymous event to google analytics '''

    if is_enabled():
        StatisticsThread(action).start()



def is_enabled():

    """ This function the activation state of the anonymous statistics feature of Autolab """

    config_section = config.get_stats_config()
    assert 'enabled' in config_section.keys(), "Missing 'enabled' parameter in section 'stats' of autolab_config.ini"

    return config_section['enabled'] == '1'





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

        # Generation of a unique anonymous identifier based on the hostname and mac address
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
            'el': __version__ # Event label
        }

        try : requests.post('https://www.google-analytics.com/collect', data=data)
        except : pass
    
    
    