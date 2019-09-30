#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import sys,os
import time

#################################################################################
############################## Connections classes ##############################
class Device_VXI11():
    def __init__(self, address, **kwargs):
        import vxi11 as v
    
        try:
            self.sock = v.Instrument(address)
        except:
            print("Wrong IP, Listening port or bad connection \nCheck cables first")
            sys.exit()
        Device.__init__(self, **kwargs)
    
    def read_raw(self):
        self.sock.read_raw()
    def write(self,string):
        "Take a sting and write it to the scope"
        self.sock.write(string)
    def read(self):
        return self.sock.read()
    def close(self):
        self.sock.close()
############################## Connections classes ##############################
#################################################################################

class Device():
    def __init__(self,nb_channels=4):
              
        self.nb_channels = int(nb_channels)
        self.type        = 'BYTE'
        
        self.write(':WAVeform:TYPE RAW')
        self.write(':WAVEFORM:BYTEORDER LSBFirst')
        self.write(':TIMEBASE:MODE MAIN')
        self.write(':WAV:SEGM:ALL ON')
        self.set_type(self.type)
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))
    
    ### User utilities
    def acquire_data_channels(self,channels=[]):
        """Get all channels or the ones specified"""
        self.stop()
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels:
            getattr(self,f'channel{i}').get_data()
            getattr(self,f'channel{i}').get_log_data()
        self.run()
        
    def save_data_channels(self,filename,channels=[],FORCE=False):
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels:
            getattr(self,f'channel{i}').save_data(filename=filename,FORCE=FORCE)
            getattr(self,f'channel{i}').save_log_data(filename=filename,FORCE=FORCE)
        
    ### Trigger functions
    def run(self):
        self.write(':RUN')
    def stop(self):
        self.write(':STOP')
    def reset(self):
        self.sock.local()
        self.sock.clear()
        self.sock.local()
        self.write('*RST')
    def idn(self):
        self.write("*IDN?")
        print(self.read())

    def set_type(self,val):
        """Argument type must be a string (BYTE or ASCII)"""
        self.type = val
        self.write(f':WAVEFORM:FORMAT {self.type}')
    def get_type(self):
        return self.type

class Channel():
    def __init__(self,dev,channel):
        self.channel = int(channel)
        self.dev     = dev
        
    def acquire_data(self):
        self.dev.write(f':WAVEFORM:SOURCE CHAN{self.channel}')
        self.dev.write(':WAV:DATA?')
        self.data = self.dev.read_raw()
        if self.dev.type == "BYTE":
            self.data = self.data[10:]
    def acquire_log_data(self):
        self.dev.write(f':WAVEFORM:SOURCE CHAN{self.channel}')
        self.dev.write(f':WAVEFORM:PREAMBLE?')
        self.log_data = self.dev.read()
    
    def get_data(self):
        return self.data
    def get_log_data(self):
        return self.log_data
    
    def save_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_DSACHAN{self.channel}'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        f = open(temp_filename,'wb')# Save data
        f.write(self.data)
        f.close()
    def save_log_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_DSACHAN{self.channel}.log'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        f = open(temp_filename,'w')
        f.write(self.log_data)
        f.close()
    
    def get_data_numerical(self):
        return array_of_float
    def save_data_numerical(self):
        return array_of_float


if __name__ == '__main__':
    from optparse import OptionParser
    import inspect
    
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
    assert 'Device_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Device_')])
    Device_LINK = getattr(sys.modules[__name__],'Device_'+options.link)
    I = Device_LINK(address=options.address)

    if options.type:
        I.set_type(options.type)
        
    t = time.time()
    ### Acquire ###
    if options.MEAS:
        for i in range(options.MEAS):
            I.stop()
            print(str(i+1))
            I.acquire_data_channels(channels=chan)
            I.save_data_channels(channels=chan,filename=str(i+1),FORCE=options.force)
            I.run()
            time.sleep(0.050)
    else:
        I.stop()
        print('trying to get channel',chan[i])
        I.acquire_data_channels(channels=chan)
        I.save_data_channels(channels=chan,filename=options.filename,FORCE=options.force)
    
    print('Measurment time', time.time() - t)
    
    I.run()
    I.close()
    sys.exit()

    

    
