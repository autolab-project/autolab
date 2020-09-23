# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 15:29:02 2020

@author: qchat
"""

import os

def process_all_changes() :

    ''' Apply all changes '''

    rename_old_devices_config_file()
    update_autolab_config()


def rename_old_devices_config_file() :

    ''' Rename local_config.ini into devices_config.ini'''

    from .paths import USER_FOLDER
    if os.path.exists(os.path.join(USER_FOLDER,'local_config.ini')) :
        os.rename(os.path.join(USER_FOLDER,'local_config.ini'),
                        os.path.join(USER_FOLDER,'devices_config.ini'))
        
def update_autolab_config():
    
    ''' In the Autolab config file, rename 'stats' section into 'telemetry' '''
    
    from .paths import AUTOLAB_CONFIG
    if os.path.exists(AUTOLAB_CONFIG) :
        import configparser
        autolab_config = configparser.ConfigParser()
        autolab_config.read(AUTOLAB_CONFIG)
        if autolab_config.has_section('stats') :
            autolab_config.add_section('telemetry')
            for item in autolab_config.items('stats') : 
                autolab_config.set('telemetry', item[0], item[1])
            autolab_config.remove_section('stats')
            with open(AUTOLAB_CONFIG, 'w') as file:
                autolab_config.write(file)

                
