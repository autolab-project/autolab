#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""

import autolab
import argparse

def main() :
    
    # Parser configuration
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", dest="help", action='store_true', help='Address of the element to open')
    parser.add_argument("-r", "--report", dest="report", action='store_true', help='Value to set')
    
    # Results
    args = parser.parse_args()
    
    # Execute order
    if args.help is True : 
        # Open help on read the docs
        autolab.help()
        
    if args.report is True : 
        # Open report issue page on github
        autolab.report()
        
    if args.help is False and args.report is False :
        # Open GUI
        autolab.gui()
                
if __name__ == '__main__' : 
    main()