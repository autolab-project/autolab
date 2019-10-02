#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

from optparse import OptionParser
import sys
import time
import visa as v

# Refer to section 3 of manual for GPIB configuration

# Get functions not available for instrument
# default GPIB address


class Device():
    def __init__(self, address='GPIB::7::INSTR'):
        ### establish GPIB communication ###
        r = v.ResourceManager()
        self.scope = r.get_instrument(address)


    #####################  FUNCTIONS ##############################################
    def modify_frequency(self, set_frequency):
        self.write('FR' + set_frequency + 'HZ')
        print('Frequency: ' + set_frequency)

    def modify_rfamp(self, set_amplitude):
        self.write('AP' + set_amplitude + 'MV')
        print('RF amplitude: ' + set_amplitude)

    def RFdisable(self):
        self.write('R2')

    def RFenable(self):
        self.write('R3')

    #####################  BASICS FUNCTIONS #######################################
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
    def close(self):
        pass


if __name__ == '__main__':
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
    I = Device(address=options.address)
    
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
