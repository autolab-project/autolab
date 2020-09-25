#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    def __init__(self,nb_channels=2):
        
        self.nb_channels = int(nb_channels)
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))
        
    
    def idn(self):
        return self.query('*IDN?')
        
    def get_driver_model(self):
        model = []
        for i in range(1,self.nb_channels+1):
            model.append({'element':'module','name':f'channel{i}','object':getattr(self,f'channel{i}'), 'help':'Channels to address command to'})
        return model


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='TCPIP::192.168.0.3::INSTR', **kwargs):
        import visa as v
        
        rm        = v.ResourceManager()
        self.inst = rm.get_instrument(address)
        Driver.__init__(self, **kwargs)
        
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        rep = self.inst.read()
        return rep
    def close(self):
        self.write(':SYST:COMM:RLST LOC')
        self.inst.close()
############################## Connections classes ##############################
#################################################################################


class Channel():
    def __init__(self,dev,channel):
        self.channel = int(channel)
        self.dev     = dev


    def arbitrary_mode(self,waveform,round_factor=4):
        assert len(waveform) <= 524288, "Don't overcome Sample max of 524288"
        waveform = ''.join([str(round(waveform[i],round_factor))+',' for i in range(len(waveform))])[:-1]
        self.dev.write(f'DATA{self.channel} VOLATILE,{waveform}')
    def amplitude(self,amplitude):
        self.dev.write(f':VOLT{self.channel} {amplitude}')
    def offset(self,offset):
        self.dev.write(f':VOLT{self.channel}:OFFS {offset}')
    def frequency(self,frequency):
        self.dev.write(f':FREQ{self.channel} {frequency}')
    
    def set_mode(self,mode_name):
        self.dev.write(f':FUNC{self.channel} {mode_name}')
    def get_mode(self):
        return self.dev.query(f':FUNC{self.channel}?')
    
    def set_pulse_duty_cycle(self,pulse_duty_cycle):
        self.dev.write(f':PULS:DCYC{self.channel} {pulse_duty_cycle}')
    def set_pulse_width(self,pulse_width):
        self.dev.write(f':PULS:WIDT{self.channel} {pulse_width}')
    

    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'mode','write':self.set_mode,'read':self.get_mode,'type':str,'help':"Set the instrument operation mode (possibilities are: SIN, SQU, RAMP, PULS, NOIS, DC, USER). Note: use USER for arbitrary functions"})
        model.append({'element':'variable','name':'pulse_duty_cycle','write':self.set_pulse_duty_cycle,'unit':'percent','type':float,'help':"Set the duty cycle for pulse mode"})
        model.append({'element':'variable','name':'pulse_width','write':self.set_pulse_width,'unit':'s','type':float,'help':"Set the pulse width for pulse mode"})
        model.append({'element':'variable','name':'amplitude','write':self.amplitude,'unit':'V','type':float,'help':"Set the amplitude"})
        model.append({'element':'variable','name':'offset','write':self.offset,'unit':'V','type':float,'help':"Set the offset"})
        model.append({'element':'variable','name':'frequency','write':self.frequency,'unit':'Hz','type':float,'help':"Set the frequency"})

        return model
    
    
    
