#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    category = 'Function generator'
    
    def __init__(self):
        pass
    
    
    def amplitude(self,amplitude):
        self.write(f'POW {amplitude}')
    def frequency(self,frequency):
        self.write(f'FREQ {frequency}')

    def idn(self):
        self.write('*IDN?')
        self.read()

#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='TCPIP::192.168.0.3::INSTR', **kwargs):
        import visa as v
        
        rm        = v.ResourceManager()
        self.inst = rm.get_instrument(address)
        Driver.__init__(self, **kwargs)
        
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        return self.inst.read()
    def close(self):
        self.inst.close()
############################## Connections classes ##############################
#################################################################################

            
if __name__ == '__main__':
    
    from optparse import OptionParser
    import inspect
    import sys
    
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
    parser.add_option("-i", "--address", type="str", dest="address", default='TCPIP::192.168.0.3::INSTR', help="Set the Ip address to use for communicate." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    I = Driver(address=options.address)

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
