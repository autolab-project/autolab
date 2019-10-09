# -*- coding: utf-8 -*-

from argparse import ArgumentParser
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
    
    configparser = index.load(PATHS)
    print(configparser.keys(),configparser.sections(),configparser)
    
    load_device(configparser,name)
    
    # Parser configuration
    parser = ArgumentParser()
    parser.add_argument("-l", "--link", type=str, dest="link", default='VISA', help="Set the link to use for the connection." )
    parser.add_argument("-i", "--address", type=str, dest="address", default='192.168.0.2', help="Set the address to use for the communication." )
    parser.add_argument("-c", "--command", nargs='+', dest="command", default=None, help="Set the command to use." )
        
    args = parser.parse_args()
    
    # Load element
    address = args.element[0].split('.')
    assert address[0] in autolab.devices.list(), f"Device {address[0]} doesn't exist"
    device = getattr(autolab.devices,address[0])
    element = device
    if len(address) > 1 :
        for i in range(1,len(address)):
            element = getattr(element,address[i])

    
    
    # instatiate the Driver_parser class with arguments(parser)
    
    


def load_device(configparser,name):
    
    """ This function tries to load the devices with the following name """
    
    # Load corresponding index
    section = configparser[name]
    list_device_attr = [key for key in configparser[section].keys()]
    
    
    
    # Driver provided
    if 'driver' not in index.keys():
        pass
        # assert address and communication arguments do exist
        #parse address and communication arguments
    else:
        driverName = index['driver']
    
    # Driver existence
    assert driverName in drivers.list()
    driver = getattr(drivers,driverName)
        
    # Check if Driver class exists in the driver
    assert 'connection' in index.keys(), f"Device index: Missing connection type for device '{name}'"
    connection = index['connection']
    assert connection in driver._getConnectionNames(),f"Device index: Wrong connection type for device '{name}'"
    driverClass = driver._getConnectionClass(connection)

    # kwargs creation
    kwargs = dict(index)
    del kwargs['driver']
    del kwargs['connection']
    
    # Instantiation of the driver
    instance = driverClass(**kwargs)
    
    # Driver modeling
    self._dev[name].load(instance)

