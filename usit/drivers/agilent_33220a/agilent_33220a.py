#!/usr/bin/env python3

import visa as v
from optparse import OptionParser
import sys
import time
from numpy import zeros,ones,linspace

ADDRESS = 'TCPIP::172.24.23.119::INSTR'

class Device():
    def __init__(self,address=ADDRESS):
        
        rm = v.ResourceManager('@py')
        self.inst = rm.get_instrument(address)
    
    
    def amplitude(self,amplitude):
        self.write('VOLT '+amplitude)
    def offset(self,offset):
        self.write('VOLT:OFFS '+offset)
    def frequency(self,frequency):
        self.write('FREQ '+frequency)
    def ramp(self,ramp):
        l   = list(zeros(5000) - 1)
        lll = list(ones(5000))
        ll  = list(linspace(-1,1,100+ramp))
        l.extend(ll);l.extend(lll)
        s = str(l)[1:-1]
        self.write('DATA VOLATILE,'+s)
    
    
    def close(self):
        #self.inst.close()
        pass
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        rep = self.inst.read()
        return rep
    def idn(self):
        self.inst.write('*IDN?')
        self.read()
        
            
if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               
               EXAMPLES:
                   
                

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-r", "--ramp", type="float", dest="ramp", default=None, help="Turn on ramp mode." )
    parser.add_option("-o", "--offset", type="str", dest="off", default=None, help="Set the offset value." )
    parser.add_option("-a", "--amplitude", type="str", dest="amp", default=None, help="Set the amplitude." )
    parser.add_option("-f", "--frequency", type="str", dest="freq", default=None, help="Set the frequency." )
    parser.add_option("-i", "--address", type="str", dest="address", default=ADDRESS, help="Set the Ip address to use for communicate." )
    (options, args) = parser.parse_args()
    
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
    if options.ramp:
        I.ramp(options.ramp)
    
    I.close()
    sys.exit()
