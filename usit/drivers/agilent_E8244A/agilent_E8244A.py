#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import visa as v
from optparse import OptionParser
import sys
import time
from numpy import zeros,ones,linspace


class Device():
    def __init__(self,address='TCPIP::169.254.54.215::INSTR'):

        rm = v.ResourceManager()
        self.inst = rm.get_instrument(address)


    def amplitude(self,amplitude):
        self.inst.write('POW '+amplitude)
    def frequency(self,frequency):
        self.inst.write('FREQ '+frequency)

    def write(self,query):
        self.inst.write(query)
    def read(self):
        rep = self.inst.read()
        return rep
    def close(self):
        pass
    def idn(self):
        self.inst.write('*IDN?')
        self.read()
            
            
if __name__ == '__main__':
    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_agilentE8244A -f 80MHz -a 20
                   
                   Set the frequency to 80MHz and the power to 20dBm.
               """
               
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-o", "--offset", type="str", dest="off", default=None, help="Set the offset value." )
    parser.add_option("-a", "--amplitude", type="str", dest="amp", default=None, help="Set the amplitude." )
    parser.add_option("-f", "--frequency", type="str", dest="freq", default=None, help="Set the frequency." )
    parser.add_option("-i", "--address", type="str", dest="address", default='TCPIP::169.254.54.215::INSTR', help="Set the Ip address to use for communicate." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    I = Device(address=options.address)

    if options.query:
        print('\nAnswer to query:',options.query)
        I.write(options.query)
        rep = I.read()
        print(rep,'\n')
        sys.exit()
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
        sys.exit()
    
    if options.amplitude:
        I.amplitude(options.amplitude)
    if options.frequency:
        I.frequency(options.frequency)
       
    I.close()
    sys.exit()
