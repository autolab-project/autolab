# -*- coding: utf-8 -*-

import configparser
import os

DRIVERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),'drivers')
USER_FOLDER_PATH = os.path.join(os.path.expanduser('~'),'autolab')
USER_LAST_CUSTOM_FOLDER_PATH = os.path.expanduser('~')
DEVICES_INDEX_PATH = os.path.join(USER_FOLDER_PATH,'devices_index.ini')
TEMPLATE_FILES_PATH = os.path.dirname(__file__)

def load():
    
    """ Returns the content of the DeviceIndex .ini file  """
    
    index = configparser.ConfigParser()
    index.read(DEVICES_INDEX_PATH)
    assert len(set(index.sections())) == len(index.sections()), "Device index: 2 devices cannot have the same name."
    return index

