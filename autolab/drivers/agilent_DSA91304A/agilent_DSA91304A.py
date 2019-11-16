#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import os
from numpy import frombuffer,int8,ndarray


class Driver():
    
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
    def get_data_channels(self,channels=[]):
        """Get all channels or the ones specified"""
        self.stop()
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels:
            getattr(self,f'channel{i}').get_data_raw()
            getattr(self,f'channel{i}').get_log_data()
        self.run()
        
    def save_data_channels(self,filename,channels=[],FORCE=False):
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels:
            getattr(self,f'channel{i}').save_data_raw(filename=filename,FORCE=FORCE)
            getattr(self,f'channel{i}').save_log_data(filename=filename,FORCE=FORCE)
        
    ### Trigger functions
    def run(self):
        self.write(':RUN')
    def stop(self):
        self.write(':STOP')
    def single(self):
        self.write('SINGLE')
    def reset(self):
        self.sock.local()
        self.sock.clear()
        self.sock.local()
        self.write('*RST')
    def idn(self):
        self.write("*IDN?")
        return self.read()

    def set_type(self,val):
        """Argument type must be a string (BYTE or ASCII)"""
        self.type = val
        self.write(f':WAVEFORM:FORMAT {self.type}')
    def get_type(self):
        return self.type
    
    
    def get_driver_model(self):
        model = []
        for i in range(1,self.nb_channels+1):
            model.append({'element':'module','name':f'channel{i}','object':getattr(self,f'channel{i}'), 'help':'Channels'})
        model.append({'element':'variable','name':'encoding','write':self.set_type,'read':self.get_type, 'type':str,'help':'Set the data encoding too use. Accepted values are: BYTE, ASCII. Default value is BYTE'})
        model.append({'element':'action','name':'stop','do':self.stop,'help':'Set stop mode for trigger'})
        model.append({'element':'action','name':'run','do':self.run,'help':'Set run mode for trigger'})
        model.append({'element':'action','name':'single','do':self.single,'help':'Set single mode for trigger'})
        return model
    
#################################################################################
############################## Connections classes ##############################
class Driver_VXI11(Driver):
    def __init__(self, address='192.168.0.14', **kwargs):
        import vxi11 as v
    
        self.sock = v.Instrument(address)
            
        Driver.__init__(self, **kwargs)
    
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


class Channel():
    def __init__(self,dev,channel):
        self.channel = int(channel)
        self.dev     = dev
        
    def get_data_raw(self):
        self.dev.write(f':WAVEFORM:SOURCE CHAN{self.channel}')
        self.dev.write(':WAV:DATA?')
        self.data_raw = self.dev.read_raw()
        if self.dev.type == "BYTE":
            self.data_raw = self.data_raw[10:]
        return self.data_raw
    def get_log_data(self):
        self.dev.write(f':WAVEFORM:SOURCE CHAN{self.channel}')
        self.dev.write(f':WAVEFORM:PREAMBLE?')
        self.log_data = self.dev.read()
        return self.log_data
    def get_data(self):
        return frombuffer(self.get_data_raw(),int8)
        
    def save_data_raw(self,filename,FORCE=False):
        temp_filename = f'{filename}_DSA91304ACH{self.channel}'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        f = open(temp_filename,'wb')# Save data
        f.write(self.data_raw)
        f.close()
    def save_log_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_DSA91304ACH{self.channel}.log'
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


    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'trace_raw','type':bytes,'read':self.get_data_raw,'help':'Get the current trace in bytes'})
        model.append({'element':'variable','name':'trace','type':ndarray,'read':self.get_data,'help':'Get the current trace in a numpy array of integers'})
        return model

