#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from optparse import OptionParser
import inspect
import sys
import time

usage = """usage: %prog [options] arg
            
EXAMPLES:
get_DSA -o my_output_file 1
result in saving two files for the temporal trace of channel 1, the data and the scope parameters, called respectively my_output_file_DSACHAN1 and my_output_file_DSACHAN1.log

get_DSA -o my_output_file 1,2
Same as previous one but with 4 output files, two for each channel (1 and 2)


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
parser.add_option("-o", "--filename", type="string", dest="filename", default='DEFAULT', help="Set the name of the output file" )
parser.add_option("-m", "--measure", type="int", dest="measure", default=None, help="Set measurment number" )
parser.add_option("-i", "--address", type="string", dest="address", default="169.254.108.195", help="Set ip address" )
parser.add_option("-l", "--link", type="string", dest="link", default='VXI11', help="Set the connection type." )
parser.add_option("-F", "--force",action = "store_true", dest="force", default=None, help="Allows overwriting file" )
parser.add_option("-t", "--type", type="string", dest="type", default='BYTE', help="Change data encoding" )
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
    
t = time.time()
### Acquire ###
if options.MEAS:
    for i in range(options.MEAS):
        I.stop()
        print(str(i+1))
        I.get_data_channels(channels=chan)
        I.save_data_channels(channels=chan,filename=str(i+1),FORCE=options.force)
        I.run()
        time.sleep(0.050)
else:
    I.stop()
    I.get_data_channels(channels=chan)
    I.save_data_channels(channels=chan,filename=options.filename,FORCE=options.force)

print('Measurment time', time.time() - t)

I.run()
I.close()
sys.exit()




