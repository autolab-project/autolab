#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import sys
from numpy import zeros,ones,linspace




class Device():
    def __init__(self):
        pass
    def amplitude(self,amplitude):
        self.write('VOLT '+str(amplitude))
    def offset(self,offset):
        self.write('VOLT:OFFS '+str(offset))
    def frequency(self,frequency):
        self.write('FREQ '+str(frequency))
    def ramp(self,ramp):
        l   = list(zeros(5000) - 1)
        lll = list(ones(5000))
        ll  = list(linspace(-1,1,100+ramp))
        l.extend(ll);l.extend(lll)
        s = str(l)[1:-1]
        self.write('DATA VOLATILE,'+s)

    def idn(self):
        self.inst.write('*IDN?')
        self.read()
        
    def getDriverConfig(self):
        
        config = []
        
        config.append({'element':'variable','name':'amplitude','write':self.amplitude,'type':float,'help':'Amplitude'})
        config.append({'element':'variable','name':'offset','write':self.offset,'type':float,'help':'Offset'})
        config.append({'element':'variable','name':'frequency','write':self.frequency,'type':float,'help':'Frequency'})
        
        return config



#################################################################################
############################## Connections classes ##############################
class Device_VISA(Device):
    def __init__(self, address='GPIB0::2::INSTR'):
        import visa
        
        rm = visa.ResourceManager()
        self.inst = rm.get_instrument(address)
        
        Device.__init__(self)
        
    def close(self):
        self.inst.close()
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        rep = self.inst.read()
        return rep
############################## Connections classes ##############################
#################################################################################
        
    
        
if __name__ == '__main__':

    from optparse import OptionParser
    import inspect

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
    parser.add_option("-i", "--address", type="str", dest="address", default='TCPIP::172.24.23.119::INSTR', help="Set the Ip address to use for communicate." )
    parser.add_option("-l", "--link", type="string", dest="link", default='VISA', help="Set the connection type." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    classes = [name for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass) if obj.__module__ is __name__]
    assert 'Device_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Device_')])
    Device_LINK = getattr(sys.modules[__name__],'Device_'+options.link)
    I = Device_LINK(address=options.address)
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
