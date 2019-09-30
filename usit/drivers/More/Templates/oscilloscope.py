#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import sys,os
import time
from numpy import fromstring,int8,int16,float64,sign
import pandas


#################################################################################
############################## Connections classes ##############################
class Device_VISA():
    def __init__(self, address, **kwargs):
        import visa as v
        
        rm        = v.ResourceManager()
        self.inst = rm.get_instrument(address)
        Device.__init__(self, **kwargs)
        
    def query(self,command):
        self.write(command)
        return self.read()
    def read(self):
        return self.inst.read()
    def write(self,command):
        self.inst.write(command)
    def close(self):
        self.inst.close()

class Device_VXI11():
    def __init__(self, address, **kwargs):
        import vxi11 as v
    
        self.inst = v.Instrument(address)
        Device.__init__(self, **kwargs)

    def query(self, command, nbytes=100000000):
        self.write(command)
        return self.read(nbytes)
    def read(self,nbytes=100000000):
        self.inst.read(nbytes)
    def write(self,cmd):
        self.inst.write(cmd)
    def close(self):
        self.inst.close()
############################## Connections classes ##############################
#################################################################################


class Device():
    def __init__(self,nb_channels=4):
              
        self.nb_channels = int(nb_channels)
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))
    
    
    ### User utilities
    def acquire_data_channels(self,channels=[]):
        """Get all channels or the ones specified"""
        previous_trigger_state = self.get_previous_trigger_state()
        self.stop()
        self.is_stopped()
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels():
            if not(getattr(self,f'channel{i}').is_active()): continue
            getattr(self,f'channel{i}').get_data()
            getattr(self,f'channel{i}').get_log_data()
        self.set_previous_trigger_state(previous_trigger_state)
        
    def save_data_channels(self,filename,channels=[],FORCE=False):
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in self.active_channels():
            getattr(self,f'channel{i}').save_data(filename=filename,FORCE=FORCE)
            getattr(self,f'channel{i}').save_log_data(filename=filename,FORCE=FORCE)
        
    ### Trigger functions
    def single(self):
        pass
    def stop(self):
        pass
    def is_stopped(self):
        while self.query('TRMD?') != 'TRMD STOP':    # typical example
            time.sleep(0.05)
        return True
    def get_previous_trigger_state(self):
        return str(previous_trigger_state)
        
    def set_previous_trigger_state(self):
        pass
        
    ### Cross-channel settings 
    def set_encoding(self):
        return str
    def get_encoding(self):
        return str
    

class Channel():
    def __init__(self,dev,channel):
        self.channel = int(channel)
        self.dev  = dev
        self.autoscale = False
    
    
    def acquire_data(self):
        #self.dev.write(...)
        #self.data = self.dev.read()
    def get_log_data(self):
        #self.dev.write(...)
        #self.log_data = self.dev.read()
    
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
    
    # additionnal functions
    def get_min(self):
        return float
    def get_max(self):
        return float
    def get_mean(self):
        return float
       
    
    def set_autoscale_enabled(bool):
        #self.autoscale = 
        pass
    def is_autoscable_enabled():
        return bool
    def do_autoscale():
        pass
       
    def is_active():
        pass



if __name__ == '__main__':
    from optparse import OptionParser
    import inspect
    
    usage = """usage: %prog [options] arg

               EXAMPLES:
                   

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
    assert 'Device_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Device_')])
    Device_LINK = getattr(sys.modules[__name__],'Device_'+options.link)
    I = Device_LINK(address=options.address)
    
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
        I.stop()
        print('trying to get channel',chan[i])
        I.acquire_data_channels(channels=chan)
        I.save_data_channels(channels=chan,filename=options.filename,FORCE=options.force)
    
    print('Measurment time', time.time() - t)
    
    I.run()
    I.close()
    sys.exit()
