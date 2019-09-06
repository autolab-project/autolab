#!/usr/bin/env python3

import Gpib
import visa as v
from optparse import OptionParser
import sys
import time
from numpy import zeros,ones,linspace
import os

ADDRESS = 'GPIB0::19::INSTR'  # for visa not used here
NAME = 0   # board_index
PAD  = 19  # gpib address

class Device():
    def __init__(self,address=[NAME,PAD]):
        
        self.inst = Gpib.Gpib(address[0],address[1])
    
    def amplitude(self,amplitude):
        self.write('AMPL '+amplitude)
    def offset(self,offset):
        self.write('OFFS '+offset)
    def frequency(self,frequency):
        self.write('FREQ '+frequency)
    def phase(self,phase):
        self.write('PHSE '+phase)
    
    def close(self):
        """WARNING: GPIB closing is automatic at sys.exit() doing it twice results in a gpib error"""
        Gpib.gpib.close(self.inst.id)
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        return self.inst.read()
    def idn(self):
        return self.query('*IDN?')
        
            
if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_srsDS345 -f 1.4e6 -a 1.1VP -o 0.1 -p 0.1
                   set the frequency to 1.4 MHz with an amplitude of 1.1 V, an offset of 100 mV and a phase of 1 degree.
               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="command", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="query", default=None, help="Set the query to use." )
    parser.add_option("-o", "--offset", type="str", dest="offset", default=None, help="Set the offset value." )
    parser.add_option("-a", "--amplitude", type="str", dest="amplitude", default=None, help="Set the amplitude. Note: The units can be VP(Vpp), VR (Vrms), or DB (dBm)." )
    parser.add_option("-f", "--frequency", type="str", dest="frequency", default=None, help="Set the frequency." )
    parser.add_option("-p", "--phase", type="str", dest="phase", default=None, help="Set the phase." )
    parser.add_option("-i", "--address", type='str', dest="address", default='[NAME,PAD]', help="Set the GPIB address to use to communicate." )
    (options, args) = parser.parse_args()
    options.address = eval(options.address)
    
    ### Start the talker ###
    I = Device(address=options.address)
    if options.query:
        print('\nAnswer to query:',options.query)
        rep = I.query(options.query)
        print(rep,'\n')
        sys.exit()
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
        sys.exit()
    
    if options.amplitude:
        I.amplitude(options.amplitude)
    if options.offset:
        I.offset(options.offset)
    if options.frequency:
        I.frequency(options.frequency)
    if options.phase:
        I.phase(options.phase)
    
    sys.exit()

