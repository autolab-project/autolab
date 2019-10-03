#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import os
import time
from numpy import frombuffer,int8


class Driver():
    
    category = 'Oscilloscope'
    
    def __init__(self,nb_channels=4):
        
        self.nb_channels = int(nb_channels)
        
        self.write('HORizontal:RECOrdlength?')
        length = self.read()
        self.write('DAT:STAR 1')
        self.write('DAT:STOP '+str(length))
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))
    
    
    ### User utilities
    def get_data_channels(self,channels=[]):
        """Get all channels or the ones specified"""
        self.stop()
        while not self.is_stopped():time.sleep(0.05)
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels():
            getattr(self,f'channel{i}').get_data_raw()
            getattr(self,f'channel{i}').get_log_data()
        self.run()
        
    def save_data_channels(self,filename,channels=[],FORCE=False):
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels():
            getattr(self,f'channel{i}').save_data_raw(filename=filename,FORCE=FORCE)
            getattr(self,f'channel{i}').save_log_data(filename=filename,FORCE=FORCE)
        
    ### Trigger functions
    def run(self):
        self.write('ACQUIRE:STATE ON')
    def stop(self):
        self.write('ACQUIRE:STATE OFF')
    def is_stopped(self):
        return '0' in self.query('ACQUIRE:STATE?')

#################################################################################
############################## Connections classes ##############################
class Driver_VXI11(Driver):
    def __init__(self, address='192.168.0.1', **kwargs):
        import vxi11 as v
    
        self.inst = v.Instrument(address)
        Driver.__init__(self, **kwargs)

    def query(self, command):
        self.write(command)
        return self.read()
    def read(self):
        self.inst.read()
    def read_raw(self):
        self.inst.read_raw()
    def write(self,cmd):
        self.inst.write(cmd)
    def close(self):
        self.inst.close()
############################## Connections classes ##############################
#################################################################################


class Channel():
    def __init__(self,dev,channel):
        self.channel = int(channel)
        self.dev  = dev


    def get_data_raw(self):
        self.dev.write(f'DAT:SOU CH{self.channel}')
        self.dev.write('DAT:ENC FAS')
        self.dev.write('CURV?')
        self.data_raw = self.dev.read_raw()
        self.data_raw = self.data_raw[:-1]
        return self.data_raw
    def get_log_data(self):
        self.dev.write(f'DAT:SOU CH{self.channel}')
        self.dev.write('WFMO?')
        self.log_data = self.dev.read()
        return self.log_data     
    def get_data(self):
        return frombuffer(self.get_data_raw(),int8)

        
    def save_data_raw(self,filename,FORCE=False):
        temp_filename = f'{filename}_DPO4104CH{self.channel}'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        f = open(temp_filename,'wb')# Save data
        f.write(self.data_raw)
        f.close()
    def save_log_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_DPO4004CH{self.channel}.log'
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
    import sys
    
    usage = """usage: %prog [options] arg

               EXAMPLES:
                   DPO4104 1 -o filename
               Record the first channel and create two files name filename_DPO4104CH1 and filename_DPO4104CH1.log
               
               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-i", "--address", type="string", dest="address", default='192.168.0.4', help="Set ip address." )
    parser.add_option("-l", "--link", type="string", dest="link", default='VXI11', help="Set the connection type." )
    parser.add_option("-F", "--force",action = "store_true", dest="force", default=None, help="Allows overwriting file" )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
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
    
    if query:
        print('\nAnswer to query:',query)
        rep = I.query(query)
        print(rep,'\n')
        sys.exit()
    elif command:
        print('\nExecuting command',command)
        I.write(command)
        print('\n')
        sys.exit()
        
    ### Acquire ###
    if options.filename:
        I.get_data_channels(channels=chan)
        I.save_data_channels(channels=chan,filename=options.filename,FORCE=options.force)
    
    print('Measurment time', time.time() - t)
    
    I.close()
    sys.exit()
