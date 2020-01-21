#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- Wavemaster 8620A
- Waverunner 104Xi
- Waverunner 6050A
"""

import os
import time
from numpy import int8,int16,frombuffer
import numpy as np


class Driver():
    
    def __init__(self,nb_channels=4):
        
        self.nb_channels = int(nb_channels)
        self.encoding    = 'BYTE'
        
        self.write('CFMT DEF9,'+self.encoding+',BIN')
        self.write('CHDR SHORT')
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))
    
    
    ### User utilities
    def get_data_channels(self,channels=[],single=False):
        """Get all channels or the ones specified"""
        previous_trigger_state = self.get_previous_trigger_state()
        self.stop()
        if single: self.single()
        while not self.is_stopped(): time.sleep(0.05)
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels:
            if not(getattr(self,f'channel{i}').is_active()): continue
            getattr(self,f'channel{i}').get_data_raw()
            getattr(self,f'channel{i}').get_log_data()
        self.set_previous_trigger_state(previous_trigger_state)
        
    def save_data_channels(self,filename,channels=[],FORCE=False):
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels:
            getattr(self,f'channel{i}').save_data_raw(filename=filename,FORCE=FORCE)
            getattr(self,f'channel{i}').save_log_data(filename=filename,FORCE=FORCE)
        
    ### Trigger functions
    def single(self):
        self.write("TRMD SINGLE")
    def stop(self):
        self.write("TRMD STOP")
    def auto(self):
        self.write("TRMD AUTO")
    def normal(self):
        self.write("TRMD NORMAL")
    def is_stopped(self):
        return 'STOP' in self.query('TRMD?')
    def get_previous_trigger_state(self):
        return self.query('TRMD?')
        
    def set_previous_trigger_state(self,previous_trigger_state):
        self.write(previous_trigger_state)
        
    ### Cross-channel settings 
    def set_encoding(self,encoding):
        self.encoding = encoding
        self.write('CFMT DEF9,'+self.encoding+',BIN')
    def get_encoding(self):
        return self.encoding
  
    def get_driver_model(self):
        
        model = []
        for num in range(1,self.nb_channels+1) :
            model.append({'element':'module','name':f'channel{num}','object':getattr(self,f'channel{num}')})
        
        model.append({'element':'variable','name':'is_stopped','read':self.is_stopped, 'type':bool,'help':'Query whether scope is stopped'})
        model.append({'element':'variable','name':'encoding','write':self.set_encoding,'read':self.get_encoding, 'type':str,'help':'Set the data encoding too use. Accepted values are: BYTE, WORD, ... Default value is BYTE'})
        model.append({'element':'action','name':'single','do':self.single,'help':'Set single mode for trigger'})
        model.append({'element':'action','name':'stop','do':self.stop,'help':'Set stop mode for trigger'})
        model.append({'element':'action','name':'auto','do':self.auto,'help':'Set auto mode for trigger'})
        model.append({'element':'action','name':'normal','do':self.normal,'help':'Set normal mode for trigger'})
        return model
    
#################################################################################
############################## Connections classes ##############################
#class Driver_VISA(Driver):
    #def __init__(self, address='GPIB0::2::INSTR', **kwargs):
        #import visa as v
        
        #rm        = v.ResourceManager()
        #self.inst = rm.get_instrument(address)
        #Driver.__init__(self, **kwargs)
    
    #def query(self,command):
        #self.write(command)
        #return self.read()
    #def read(self):
        #return self.inst.read()
    #def read_raw(self):
        #return self.inst.read_raw()
    #def write(self,command):
        #self.inst.write(command)
    #def close(self):
        #self.inst.close()

class Driver_VXI11(Driver):
    def __init__(self, address='192.168.0.1', **kwargs):
        import vxi11 as v
    
        self.inst = v.Instrument(address)
        Driver.__init__(self, **kwargs)

    def query(self, command, nbytes=100000000):
        self.write(command)
        return self.read(nbytes)
    def read(self,nbytes=100000000):
        return self.inst.read(nbytes)
    def read_raw(self):
        return self.inst.read_raw()
    def write(self,cmd):
        self.inst.write(cmd)
    def close(self):
        self.inst.close()
############################## Connections classes ##############################
#################################################################################


class Channel():
    def __init__(self,dev,channel):
        self.channel          = int(channel)
        self.dev              = dev
        self.autoscale        = False
        self.autoscale_factor = 8
    
    
    def get_data_raw(self):
        if self.autoscale:
            self.do_autoscale()
        self.dev.write(f'C{self.channel}:WF? DAT1')
        self.data_raw = self.dev.read_raw()
        self.data_raw = self.data_raw[self.data_raw.find(b'#')+11:-1]
        return self.data_raw
    def get_data(self):
        if self.dev.encoding=='BYTE': return frombuffer(self.get_data_raw(),int8)
        if self.dev.encoding=='WORD': return frombuffer(self.get_data_raw(),int16)
    def get_log_data(self):
        self.log_data = self.dev.query(f"C{self.channel}:INSP? 'WAVEDESC'")
        return self.log_data
    
    
    def save_data_raw(self,filename,FORCE=False):
        temp_filename = f'{filename}_WAVEMASTERCH{self.channel}'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        f = open(temp_filename,'wb')# Save data
        f.write(self.data_raw)
        f.close()
    def save_log_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_WAVEMASTERCH{self.channel}.log'
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
        stri  = self.dev.query(f'C{self.channel}:PAVA? MIN')
        return float(stri.split(',')[1].split(' ')[0])
    def get_max(self):
        stri  = self.dev.query(f'C{self.channel}:PAVA? MAX')
        return float(stri.split(',')[1].split(' ')[0])
    def get_mean(self):
        stri = self.dev.query(f'C{self.channel}:PAVA? MEAN')
        return float(stri.split(',')[1].split(' ')[0])
        
    def set_vertical_offset(self,val):
        self.dev.write(f'C{self.channel}:OFST {val}') 
    def get_vertical_offset(self):
        return float(self.dev.query(f'C{self.channel}:OFST?').split(' ')[1])
    def set_vertical_scale(self,val):
        self.dev.write(f'C{self.channel}:VDIV {val}') 
    def get_vertical_scale(self):
        return float(self.dev.query(f'C{self.channel}:VDIV?').split(' ')[1])
        
    def do_autoscale(self):
        fact       = 0
        target     = self.autoscale_factor * 0.1
        acceptance = 0.05
        
        mi = self.get_min()
        ma = self.get_max()
        val = round((-1)*(mi+ma)/2.,3)
        self.set_vertical_offset(val)
        VDIV = self.get_vertical_scale()
        OFST = self.get_vertical_offset()
        R_MI = -(5*VDIV)-OFST
        R_MA =   5*VDIV -OFST
        r_diff = R_MA - R_MI
        fact = (ma-mi)/r_diff
        
        k = 1
        while abs(target-fact)>acceptance or mi<R_MI or ma>R_MA or abs(R_MI-mi)<0.10*VDIV*10:            
            # compute new channel amplitude as distance from target
            new_channel_amp  = VDIV + VDIV * round(fact-target,3)
            if mi<R_MI or ma>R_MA or abs(R_MI-mi)<0.10*VDIV*10:
                new_channel_amp = new_channel_amp + new_channel_amp * 0.5                    
            if new_channel_amp<0.005: new_channel_amp = 0.005 # if lower than the lowest possible 5mV/div
            self.set_vertical_scale(new_channel_amp)  # set_vertical_scale do change vertical_offset...
            self.set_vertical_offset(val)             # must do this then
            
            # trig for a eventual new iteration
            self.dev.single()
            print(f'Optimisation loop, index: {k}, distance from target ({acceptance}): {round(abs(target-fact),3)}')
            k = k + 1
            
            mi = self.get_min()
            ma = self.get_max()
            val = round((-1)*(mi+ma)/2.,3)
            self.set_vertical_offset(val)
            VDIV = self.get_vertical_scale()
            OFST = self.get_vertical_offset()
            R_MI = -(5*VDIV)-OFST
            R_MA =   5*VDIV -OFST
            r_diff = R_MA - R_MI
            fact = (ma-mi)/r_diff
            
            
    def set_autoscale_enable(self):
        self.autoscale = True
    def set_autoscale_disable(self):
        self.autoscale = False
    def set_autoscale_factor(self,val):
        self.autoscale_factor = float(val)
    def get_autoscale_factor(self):
        return self.autoscale_factor
           
    def is_active(self):
        temp = self.dev.query(f'C{self.channel}:TRA?')
        return 'ON' in temp



    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'min','type':float,'unit':'V','read':self.get_min,'help':'Get minimum value of the current signal'})
        model.append({'element':'variable','name':'max','type':float,'unit':'V','read':self.get_max,'help':'Get maximum value of the current signal'})
        model.append({'element':'variable','name':'mean','type':float,'unit':'V','read':self.get_mean,'help':'Get mean value of the current signal'})
        model.append({'element':'variable','name':'trace_raw','type':bytes,'read':self.get_data_raw,'help':'Get the current trace in bytes'})
        model.append({'element':'variable','name':'trace','type':np.ndarray,'read':self.get_data,'help':'Get the current trace in numpy'})
        model.append({'element':'variable','name':'vertical_scale','type':float,'unit':'V/div','read':self.get_vertical_scale,'write':self.set_vertical_scale,'help':'Set the vertical scale of the channel'})
        model.append({'element':'variable','name':'vertical_offset','type':float,'unit':'V','read':self.get_vertical_offset,'write':self.set_vertical_offset,'help':'Set the vertical offset of the channel'})
        model.append({'element':'variable','name':'autoscale_factor','type':float,'read':self.get_autoscale_factor,'write':self.set_autoscale_factor,'help':'For setting limits of the vertical scale, units are in number of scope divisions here. WARNING: code security avoid traces too close from screen extrema (at 9 divisions) and result in endless looping. WARNING: the number of vertical divisions might depend on the scope (8 or 10 usually)." '})
        model.append({'element':'variable','name':'active','type':bool,'read':self.is_active,'help':'Returns the current state of the channel.'})
        model.append({'element':'action','name':'autoscale_enable','do':self.set_autoscale_enable,'help':'Enable autoscale mode. This will work best if your scope triggers (i.e. not on AUTO trigger mode with no relevant trigger signal).'})
        model.append({'element':'action','name':'autoscale_disable','do':self.set_autoscale_disable,'help':'Disnable autoscale mode.'})
        return model


   

