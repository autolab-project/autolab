# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""


def list() :
    
    import os

    return [name for name in os.listdir(os.path.dirname(__file__)) 
            if os.path.isdir(os.path.join(os.path.dirname(__file__),name)) and
             f'{name}.py' in os.listdir(os.path.join(os.path.dirname(__file__),name))]



#

