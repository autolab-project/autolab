# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 09:35:03 2019

@author: quentin.chateiller
"""


# FOR PARSER USE

# python usit.py -e mydummy.amplitude -p        GET AND SAVE VARIABLE VALUE
# python usit.py -e mydummy.something           EXECUTE ACTION
# python usit.py -e mydummy.amplitude -v 4      SET VARIABLE VALUE

import usit
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-e", "--element", type="str", dest="element", default=None, help='Element to open' )
parser.add_option("-v", "--value", type="str", dest="value", default=None, help='Value to set' )
parser.add_option("-p", "--path", type="str", dest="path", default=None, help='Path where to save data' )
(options, args) = parser.parse_args()

if options.element is not None :  
    address = options.element.split('.')
    assert address[0] in usit.devices.list()
    device = getattr(usit.devices,address[0])
    obj = device
    if len(address) > 1 :
        for i in range(1,len(address)):
            obj = getattr(obj,address[i])
    if options.path is not None: 
        obj.save(options.path)
    elif options.value is not None :
        obj(options.value)
    else :
        obj()
    device.close()

