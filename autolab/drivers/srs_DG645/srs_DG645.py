#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    def __init__(self):
        
        self.conv = ['T0','T1','A','B','C','D','E','F','G','H']
        self.conv2 = ['T0','AB','CD','EF','GH']
        self.delay_channels = ''
        
        for i in self.conv2:
            setattr(self,f'output{i}',Output(self,i))
    
        
    def set_frequency(self,frequency):
        self.write(f'TRAT{frequency}')
    def get_frequency(self):
        return float(self.query('TRAT?'))
    
    def set_delay_channels(self,channels):
        assert len(channels)==1 or len(channels)==2, f"Argument channels must be a str of length either 1 or 2 in {self.conv[2:]}"
        self.delay_channels = channels
        
    def set_delay(self, delay,channels=None):
        if channels is None: channels = self.delay_channels
        assert len(channels)==1 or len(channels)==2, "You may want to set_delay_channels first"
        if len(channels) == 2:
            ch1 = str(self.conv.index(channels[0]))
            ch2 = str(self.conv.index(channels[1]))
        elif len(channels) == 1:
            ch1 = '0'
            ch2 = str(self.conv.index(channels))
        self.write(f'DLAY{ch2},{ch1},{delay}')

    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'frequency','type':float,'unit':'Hz','write':self.set_frequency,'read':self.get_frequency,'help':'Output frequency.'})
        return model
        
#################################################################################
############################## Connections classes ##############################
class Driver_VXI11(Driver):
    def __init__(self,address='192.168.0.4', **kwargs):
        import vxi11 as v

        self.inst = v.Instrument(address)
        Driver.__init__(self)

    def query(self, cmd, nbytes=1000000):
        """Send command 'cmd' and read 'nbytes' bytes as answer."""
        self.write(cmd+'\n')
        r = self.read(nbytes)
        return r
    def read(self,nbytes=1000000):
        return self.inst.read(nbytes)
    def write(self,cmd):
        self.inst.write(cmd)
    def close(self):
        self.inst.close()
############################## Connections classes ##############################
#################################################################################


class Output():
    def __init__(self,dev,output):
        self.output = str(output)
        self.dev     = dev
    
    def set_amplitude(self,amplitude):
        self.dev.write(f'LAMP{self.dev.conv2.index(self.output)},{amplitude}')
    def get_amplitude(self):
        return float(self.dev.query(f'LAMP?{self.dev.conv2.index(self.output)}'))
    def set_polarity(self,polarity):
        self.dev.write(f'LPOL{self.dev.conv2.index(self.output)},{polarity:g}')
    def get_polarity(self):
        return bool(int(self.dev.query(f'LPOL?{self.dev.conv2.index(self.output)}')))
    def set_offset(self,offset):
        self.dev.write(f'LOFF{self.dev.conv2.index(self.output)},{offset}')
    def get_offset(self):
        return float(self.dev.query(f'LOFF?{self.dev.conv2.index(self.output)}'))
    
    def set_delay(self,delay):
        self.dev.set_delay(delay,channels=self.output)
            
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'amplitude','type':float,'unit':'V','write':self.set_amplitude,'read':self.get_amplitude,'help':'Voltage amplitude.'})
        model.append({'element':'variable','name':'polarity','type':bool,'read':self.get_polarity,'write':self.set_polarity,'help':'Polarity state.'})
        model.append({'element':'variable','name':'offset','type':float,'unit':'V','write':self.set_offset,'read':self.get_offset,'help':'Voltage offset'})
        model.append({'element':'variable','name':'delay','type':float,'unit':'s','write':self.set_delay,'help':'Set the delay between the two channels of the given output'})
        return model
    
