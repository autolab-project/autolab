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
parser.add_option("-k", "--karen", type="str", dest="kar", default=None, help="Set ON karen's measurment." )
parser.add_option("-a", "--amplitude", type="str", dest="amp", default=None, help="Set the amplitude." )
parser.add_option("-f", "--frequency", type="str", dest="freq", default=None, help="Set the frequency." )
parser.add_option("-p", "--period", type="str", dest="per", default=None, help="Set the period." )
(options, args) = parser.parse_args()

### Start the talker ###
I = Driver()

if options.kar:
    I.init_karen_meas()
    sys.exit()

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
if frequency:
    I.frequency(options.frequency)
if period:
    I.period(options.period)

I.close()
sys.exit()
