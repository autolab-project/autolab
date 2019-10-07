#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from optparse import OptionParser
import inspect
import sys

usage = """usage: %prog [options] arg

            WARNING: - Be sure all the channel you provide are active
            
            EXAMPLES:
                get_DSO54853A -o filename 1,2
            Record channel 1 and 2 and create 4 files (2 per channels) name filename_DSO54853ACH1 and filename_DSO54853ACH1.log


            IMPORTANT INFORMATIONS:
                - Datas are obtained in a binary format: int8 
                - Header is composed as follow:
                <format>, <type>, <points>, <count> , <X increment>, <X origin>, < X reference>, <Y increment>, <Y origin>, <Y reference>, <coupling>, <X display range>, <X display origin>, <Y display range>, <Y display origin>, <date>,
                <time>, <frame model #>, <acquisition mode>, <completion>, <X units>, <Y units>, <max bandwidth limit>, <min bandwidth limit>    
                - To retrieve datas (in "Units")
                Y-axis Units = data value * Yincrement + Yorigin (analog channels) 
                X-axis Units = data index * Xincrement + Xorigin

            """
parser = OptionParser(usage)
parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
parser.add_option("-i", "--address", type="string", dest="address", default='192.168.0.4', help="Set ip address" )

parser.add_option("-t", "--type", type="str", dest="type", default="BYTE", help="Type of data returned (available values are 'BYTE' or 'ASCII')" )
parser.add_option("-l", "--link", type="string", dest="link", default='VXI11', help="Set the connection type." )
parser.add_option("-F", "--force",action = "store_true", dest="force", default=None, help="Allows overwriting file" )
(options, args) = parser.parse_args()

### Compute channels to acquire ###
if (len(args) == 0) and (options.com is None) and (options.que is None):
    print('\nYou must provide at least one channel\n')
    sys.exit()
else:
    chan = [int(a) for a in args[0].split(',')]
####################################

### Start the talker ###
classes = [name for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass) if obj.__module__ is __name__]
assert 'Driver_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Driver_')])
Driver_LINK = getattr(sys.modules[__name__],'Driver_'+options.link)
I = Driver_LINK(address=options.address)

if options.type:
    I.set_type(options.type)

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

if options.filename:
    I.stop()
    I.get_data_channels(channels=chan)
    I.save_data_channels(channels=chan,filename=options.filename,FORCE=options.force)
else:
    print('If you want to save, provide an output file name')

I.run()
I.close()
sys.exit()
