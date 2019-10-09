# -*- coding: utf-8 -*-

import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)),'autolab','core'))


import paths
import index
import drivers_parser_utilities as utilities
#import config
#config.check()

PATHS = paths.Paths()

def main():
    print('ok')
    
    r = index.load(PATHS)
    print(r.keys,r)
#def main():

    ## Parser configuration
    #parser = argparse.ArgumentParser()
    #parser.add_argument('element', type=str, nargs=1, help='Address of the element to open' )
    #parser.add_argument("-v", "--value", type=str, dest="value", default=None, help='Value to set')
    #parser.add_argument("-p", "--path", type=str, dest="path", default=None, help='Path where to save data')
    
    ## Results
    #args = parser.parse_args()
    
    ## Load element
    #address = args.element[0].split('.')
    #assert address[0] in autolab.devices.list(), f"Device {address[0]} doesn't exist"
    #device = getattr(autolab.devices,address[0])
    #element = device
    #if len(address) > 1 :
        #for i in range(1,len(address)):
            #element = getattr(element,address[i])
            
    ## Execute order
    #if args.path is not None: 
        #assert element._elementType == 'Variable', f"This element is not a variable"
        #assert element.readable is True, f"This element is not readable"
        #value = element()
        #element.save(os.path.join(args.path,element.name+'.txt'),value=value)
        
    #elif args.value is not None :
        #assert element._elementType == 'Variable', f"This element is not a variable"
        #assert element.writable is True, f"This element is not writable"
        #element(args.value)
        
    #else :
        #assert element._elementType in ['Variable','Action'], f"Please provide a Variable or Action element"
        #if element._elementType == 'Variable' :
            #print(element())
        #elif element._elementType == 'Action' :
            #element()
    
    #device.close()

#def _load(self,name):
    
    #""" This function tries to load the devices with the following name """
    
    ## Load corresponding index
    #index = self._index[name]
    
    ## Driver provided
    #assert 'driver' in index.keys(), f"Device index: Missing driver for device '{name}'"
    #driverName = index['driver']
    
    ## Driver existence
    #assert driverName in drivers.list()
    #driver = getattr(drivers,driverName)
        
    ## Check if Driver class exists in the driver
    #assert 'connection' in index.keys(), f"Device index: Missing connection type for device '{name}'"
    #connection = index['connection']
    #assert connection in driver._getConnectionNames(),f"Device index: Wrong connection type for device '{name}'"
    #driverClass = driver._getConnectionClass(connection)

    ## kwargs creation
    #kwargs = dict(index)
    #del kwargs['driver']
    #del kwargs['connection']
    
    ## Instantiation of the driver
    #instance = driverClass(**kwargs)
    
    ## Driver modeling
    #self._dev[name].load(instance)

