# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""

import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)),'autolab','core'))
print(os.path.join(os.path.dirname(os.path.dirname(__file__)),'autolab','core'))
import paths

# Pas d'import autolab ici, sinon ca execute tous les __init__ sur le chemin

#from ..core import paths
#os.path.dirname(__file__)

def main():
    print('ok')
    print(paths.DRIVERS_PATH)




    
