#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from optparse import OptionParser
import inspect
import sys

usage = """usage: %prog [options] arg
            
            EXAMPLES:
                set_TTITGF3162 -f 80000000 -a 2
                set_TTITGF3162 -f 80e6 -a 2
                Note that both lines are equivalent
                
                Set the frequency to 80MHz and the power to 2Vpp.
                
                Note: Arbitrary waveform available only using a python terminal (for now)
                
            """
            
parser = OptionParser(usage)
parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
parser.add_option("-o", "--offset", type="str", dest="off", default=None, help="Set the offset value." )
parser.add_option("-a", "--amplitude", type="str", dest="amp", default=None, help="Set the amplitude." )
parser.add_option("-f", "--frequency", type="str", dest="freq", default=None, help="Set the frequency." )
parser.add_option("-i", "--address", type="str", dest="address", default='169.254.62.40', help="Set the Ip address to use for communicate." )
parser.add_option("-p", "--port", type="float", dest="port", default=9221, help="Set the port to use for communicate." )
(options, args) = parser.parse_args()

    ### Compute channels to acquire ###
if (len(args) != 1) and (options.com is None) and (options.que is None):
    print('\nYou must provide only one channel\n')
    sys.exit()
elif len(args) == 1:
    chan = []
    temp_chan = args[0].split(',')                  # Is there a coma?
    for i in range(len(temp_chan)):
        chan.append('CHN' + temp_chan[i])
else:
    print('\nYou must provide only one channel\n')
    sys.exit()
print(chan)
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
if chan:
    I.swap_channel(chan)
if options.amplitude:
    I.amplitude(options.amplitude)
if options.frequency:
    I.frequency(options.frequency)
if options.offset:
    I.offset(options.offset)

sys.exit()
