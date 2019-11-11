#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""

import autolab
import argparse
import os

# autolab-device mydummy.amplitude -p C:\Users\      GET AND SAVE VARIABLE VALUE
# autolab-device mydummy.something                   EXECUTE ACTION
# autolab-device mydummy.amplitude -v 4              SET VARIABLE VALUE
# autolab-device mydummy.amplitude -h                DISPLAY ELEMENT HELP

def main():

    # Parser configuration
    parser = argparse.ArgumentParser()
    parser.add_argument('name', type=str, nargs=1, help='Name of the device (only preconfigured instruments)' )
    parser.add_argument('-e', '--element', type=str, nargs=1, dest="element", help='Address of the element to open' )
    parser.add_argument("-v", "--value", type=str, dest="value", default=None, help='Value to set')
    parser.add_argument("-p", "--path", type=str, dest="path", default=None, help='Path where to save data')
   
    # Results
    args = parser.parse_args()
    
    # Load device
    device = autolab.get_device(args.name[0])
    
    # Find element
    element = autolab.get_element_by_address(args.name[0]+'.'+args.element[0])
        
    # Execute order
    if args.help is True :
        print(element.help())
        
    elif args.path is not None: 
        assert element._element_type == 'variable', f"This element is not a Variable"
        assert element.readable is True, f"This element is not readable"
        value = element()
        element.save(args.path,value=value)
        
    elif args.value is not None :
        if element._element_type == 'variable' :
            assert element.writable is True, f"This variable is not writable"
            element(args.value)
        elif element._element_type == 'action' :
            assert element.has_parameter, f"This action has no parameter"
            element(args.value)
        
    else :
        assert element._element_type in ['variable','action'], f"Please provide a Variable or Action element"
        if element._element_type == 'variable' :
            print(element())
        elif element._element_type == 'action' :
            element()
    
    device.close()
    
if __name__ == '__main__'  :
    main()

