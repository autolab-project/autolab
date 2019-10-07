#!/usr/bin/env python3
# -*- coding: utf-8 -*-
    
    
from optparse import OptionParser
import inspect
import sys

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
assert 'Driver_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Driver_')])
Driver_LINK = getattr(sys.modules[__name__],'Driver_'+options.link)
I = Driver_LINK(address=options.address)

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
