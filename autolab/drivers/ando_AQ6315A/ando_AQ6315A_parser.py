#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from optparse import OptionParser
import inspect
import sys

usage = """usage: %prog [options] arg

            EXAMPLES:
                get_AQ6315A -o filename A,B,C
            Record the spectrum and create files with two columns lambda,spectral amplitude

            """
parser = OptionParser(usage)
parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
parser.add_option("-i", "--address", type="string", dest="address", default='GPIB::3::INSTR', help="Set ip address." )
parser.add_option("-l", "--link", type="string", dest="link", default='VISA', help="Set the connection type." )
parser.add_option("-F", "--force",action = "store_true", dest="force", default=None, help="Allows overwriting file" )
parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
#parser.add_option("-t", "--trigger", action="store_true", dest="trigger", default=False, help="Ask the scope to trigger once before acquiring." )    # need is_scope_stopped(self) to enable triggering
(options, args) = parser.parse_args()

### Compute traces to acquire ###
if (len(args) == 0) and (options.com is None) and (options.que is None):
    print('\nYou must provide at least one trace\n')
    sys.exit()
else:
    chan = [str(a) for a in args[0].split(',') if a in ['A','B','C']]
####################################

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

if options.filename:
    I.get_data_traces(traces=chan) #,single=options.trigger)
    I.save_data_traces(options.filename,FORCE=options.force)


sys.exit()
