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

    def set_frequency(self, frequency):
        self.write('FR' + frequency + 'HZ')

    def set_rfamp(self, amplitude):
        self.write('AP' + amplitude + 'MV')

    def RFdisable(self):
        self.write('R2')

    def RFenable(self):
        self.write('R3')


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB::7::INSTR', **kwargs):
        import visa as v
        
        r = v.ResourceManager()
        self.scope = r.get_instrument(address)
        Driver.__init__(self, **kwargs)
        
    def query(self, query, length=1000000):
        self.write(query)
        r = self.read(length=length)
        return r
    def write(self, query):
        self.string = query + '\n'
        self.scope.write(self.string)
    def read(self, length=10000000):
        rep = self.scope.read_raw()
        return rep
        
############################## Connections classes ##############################
#################################################################################

if __name__ == '__main__':
    from optparse import OptionParser
    import inspect
    import sys
    
    usage = """usage: %prog [options] arg

               EXAMPLES:
               frequency(Hz):       HP86568 -f 10e6
               RF amplitude(mV):    HP86568 -a 10
               HP86568 -x
               HP86568 -z
               HP86568 -m reserved
               """
    parser = OptionParser(usage)
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use.")
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to execute.")
    parser.add_option("-i", "--address", type="str", dest="address", default='GPIB::7::INSTR', help="Set the gpib port to use.")
    parser.add_option("-f", "--frequency", type="str", dest="frequency", default=None, help="Set the carrier frequency (Hz)")
    parser.add_option("-a", "--amplitude", type="str", dest="amplitude", default=None, help="Set the carrier RF amplitude (mV)")
    parser.add_option("-x", "--RFenable", action="store_true", dest="RFenable", default=False, help="Enable RF output")
    parser.add_option("-z", "--RFdisbale", action="store_true", dest="RFdisable", default=False, help="Disable RF output")

    (options, args) = parser.parse_args()

    ### Start the talker ###
    I = Driver(address=options.address)
    
    if options.query:
        print('\nAnswer to query:', options.query)
        I.write(options.query + '\n')
        rep = I.read()
        print(rep, '\n')
    elif options.command:
        print('\nExecuting command', options.command)
        I.scope.write(options.command)
        print('\n')

    if options.amplitude:
        I.modify_rfamp(options.amplitude)
    if options.frequency:
        I.modify_frequency(str(float(options.frequency)))
    if options.RFenable:
        I.RFenable()
    elif options.RFdisable:
        I.RFdisable()
    
    I.close()
    sys.exit()
