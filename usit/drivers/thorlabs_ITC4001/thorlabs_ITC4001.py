#!/usr/bin/env python3

import visa as v 
import time as t
from numpy import *
from optparse import OptionParser
import sys

ADDRESS = 'USB0::4883::32842::M00248997::INSTR'

class Device():
    def __init__(self,address=ADDRESS):
        ### Initiate communication ###
        rm = v.ResourceManager()
        self.inst = rm.get_instrument(address)


    def amplitude(self,amplitude):
        self.write('SOUR:CURR %f\n' %amplitude)
        print('\nSetting current to: ',amplitude,'V\n')
            
    def query(self, cmd):
        self.write(cmd)
        r = self.read()
        return r
    def read(self):
        return self.inst.read()
    def write(self,cmd):
        self.inst.write(cmd+'\n')
    def close(self):
        self.inst.close()
        
if __name__=="__main__":
    
    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_ITC4001 -a val 1
               
               Set the pumping current to val to the instrument 1
               Instrument numner must be from 1 to 3 (as written on it) 

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="command", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="query", default=None, help="Set the query to use." )
    parser.add_option("-a", "--amplitude", type="float", dest="amplitude", default=None, help="Set the pumping current value")
    parser.add_option("-i", "--address", type="str", dest="address", default=ADDRESS, help="Set the USB VISA address to use for the communication")
    (options, args) = parser.parse_args()
    
    
    ### Call the class with arguments ###
    I = Device(address=options.address)

    ### Basic communications ###
    if options.query:
        print('\nAnswer to query:',options.query)
        rep = I.query(options.query)
        print(rep,'\n')
        I.close();sys.exit()
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
        I.close();sys.exit()

    ### change the value of the current ###
    if options.amplitude or options.amplitude==0:
        I.amplitude(options.amplitude)
        
    I.close()
    sys.exit()
