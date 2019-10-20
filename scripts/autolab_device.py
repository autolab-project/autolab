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
    parser.add_argument('element', type=str, nargs=1, help='Address of the element to open' )
    parser.add_argument("-v", "--value", type=str, dest="value", default=None, help='Value to set')
    parser.add_argument("-p", "--path", type=str, dest="path", default=None, help='Path where to save data')
    parser.add_argument("-h", "--help", dest="help", action='store_true', help='Display element help')
    
    # Results
    args = parser.parse_args()
    
    # Load element
    address = args.element[0].split('.')
    assert address[0] in autolab.list_devices(), f"Device {address[0]} doesn't exist"
    device = autolab.get_device(address[0])
    element = device
    if len(address) > 1 :
        for i in range(1,len(address)):
            element = getattr(element,address[i])
            
    # Execute order
    if args.help is True :
        print(element.help())
        
    elif args.path is not None: 
        assert element._element_type == 'variable', f"This element is not a Variable"
        assert element.readable is True, f"This element is not readable"
        value = element()
        element.save(os.path.join(args.path,element.name+'.txt'),value=value)
        
    elif args.value is not None :
        assert element._element_type == 'variable', f"This element is not a Variable"
        assert element.writable is True, f"This element is not writable"
        element(args.value)
        
    else :
        assert element._elementt_ype in ['variable','action'], f"Please provide a Variable or Action element"
        if element._element_type == 'variable' :
            print(element())
        elif element._element_type == 'action' :
            element()
    
    device.close()
    
if __name__ == '__main__'  :
    main()

