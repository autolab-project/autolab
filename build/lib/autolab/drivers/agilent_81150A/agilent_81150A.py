#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    category = 'Function generator'
    
    def __init__(self,nb_channels=2):
        
        self.nb_channels = int(nb_channels)
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))
        
    
    def idn(self):
        self.write('*IDN?')
        self.read()


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
        #self.inst.close()
############################## Connections classes ##############################
#################################################################################

class Channel():
    def __init__(self,dev,channel):
        self.channel = int(channel)
        self.dev     = dev
        
    def amplitude(self,amplitude):
        self.dev.write(f':VOLT{self.channel} {amplitude}')
    def offset(self,offset):
        self.dev.write(f':VOLT{self.channel}:OFFS {offset}')
    def frequency(self,frequency):
        self.dev.write(f':FREQ{self.channel} {frequency}')
    def dc_mode(self,offset):
        self.dev.write(f':FUNC{self.channel} DC')
        self.offset(offset=offset)
    def arbitrary_mode(self,waveform,round_factor=4):
        assert len(waveform) <= 524288, "Don't overcome Sample max of 524288"
        waveform = ''.join([str(round(waveform[i],round_factor))+',' for i in range(len(waveform))])[:-1]
        self.dev.write(f'DATA{self.channel} VOLATILE,{waveform}')
    def pulse_mode(self,width=None,duty_cycle=None):
        assert not(duty_cycle and width), "Please provide either duty_cycle OR width"
        self.dev.write(f':FUNC{self.channel} PULS')
        if duty_cycle: self.dev.write(f':PULS:DCYC{self.channel} {width}')
        if width:      self.dev.write(f':PULS:WIDT{self.channel} {width}')
        
        
