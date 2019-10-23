#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import os
import time
from numpy import savetxt,linspace
import pandas


class Driver():
    
    category = 'Spectrum analyser'
    #['Oscilloscope','Optical source','Spectrum analyser','Motion controller','Function generator','Power meter','Electrical source','Optical frame', 'Electrical frame','Optical shutter','PID controller','Temperature controller']
    
    def __init__(self,nb_traces=6):
              
        self.nb_traces = int(nb_traces)
        
        for i in range(1,self.nb_traces+1):
            setattr(self,f'trace{i}',Traces(self,i))
    
    
    ### User utilities
    def get_data_traces(self,traces=[],single=None):
        """Get all traces or the ones specified"""
        previous_trigger_state = self.get_previous_trigger_state()
        if single: self.single()
        self.ensure_scope_stopped()
        if traces == []: traces = list(range(1,self.nb_traces+1))
        for i in traces:
            if not(getattr(self,f'trace{i}').is_active()): continue
            getattr(self,f'trace{i}').get_data()
        self.set_previous_trigger_state(previous_trigger_state)
        
    def save_data_traces(self,filename,traces=[],FORCE=False):
        if traces == []: traces = list(range(1,self.nb_traces+1))
        for i in traces:
            getattr(self,f'trace{i}').save_data(filename=filename,FORCE=FORCE)
        
    ### Trigger functions
    def single(self):
        self.write('*TRG')
    def get_previous_trigger_state(self):
        return self.query('INIT:CONT?')
    def set_previous_trigger_state(self,previous_trigger_state):
        self.write('INIT:CONT '+previous_trigger_state)
    def ensure_scope_stopped(self):
        self.query('INIT:CONT OFF;*OPC?')
        

#################################################################################
############################## Connections classes ##############################
class Driver_VXI11(Driver):
    def __init__(self, address='192.168.0.3', **kwargs):
        import vxi11 as v
    
        self.inst = v.Instrument(address)
        Driver.__init__(self, **kwargs)

    def write(self, msg):
        self.sock.write(msg)
    def read(self):
        return self.sock.read()
    def query(self,msg):
        """Sends question and returns answer"""
        self.write(msg)
        return(self.read())
    def close(self):
        self.inst.close()
        
class Driver_GPIB(Driver):
    def __init__(self,address=2,board_index=0,**kwargs):
        import Gpib
        
        self.inst = Gpib.Gpib(int(board_index),int(address))
        Driver.__init__(self)
    
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,command):
        self.inst.write(command)
    def read(self,length=1000000000):
        return self.inst.read(length).decode().strip('\r\n') #replace \r\n with the characters at the end of the line to remove 
    def close(self):
        """WARNING: GPIB closing is automatic at sys.exit() doing it twice results in a gpib error"""
        #Gpib.gpib.close(self.inst.id)
        pass
############################## Connections classes ##############################
#################################################################################


class Traces():
    def __init__(self,dev,trace):
        self.trace     = int(trace)
        self.dev       = dev
        self.data_dict = {}
        
    def get_data(self):
        self.data        = eval(self.dev.query(f"TRAC:DATA? TRACE{self.trace}"))
        self.frequencies = self.get_frequencies(self.data)
        return self.frequencies,self.data
    def get_data_dataframe(self):
        frequencies,data              = self.get_data()
        self.data_dict['frequencies'] = self.frequencies
        self.data_dict['amplitude']   = self.data
        return pandas.DataFrame(self.data_dict)
    
    def get_start_frequency(self):
        return float(self.dev.query("SENS:FREQ:START?"))
    def get_stop_frequency(self):
        return float(self.dev.query("SENS:FREQ:STOP?"))
    def get_frequencies(self,data):
        start = self.get_start_frequency()
        stop  = self.get_stop_frequency()
        return linspace(start,stop,len(data))
    
    def save_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_MXAN9020ATR{self.trace}.txt'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        
        savetxt(temp_filename,(self.frequencies,self.data))

