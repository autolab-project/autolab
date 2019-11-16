#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import time

class Driver():
    
    def __init__(self,nb_channels=2):
        
        self.nb_channels = int(nb_channels)
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))

        
    def write_to_channel(self,channel,command):
        self.write(f'CHN {channel}')
        self.write(command)

    def idn(self):
        return self.query('*IDN?')
        
        
    def get_driver_model(self):
        model = []
        for num in range(1,self.nb_channels+1) :
            model.append({'element':'module','name':f'channel{num}','object':getattr(self,f'channel{num}')})
        return model

#################################################################################
############################## Connections classes ##############################
class Driver_SOCKET(Driver):
    def __init__(self,address='169.254.62.40',port=9221, **kwargs):
        import socket
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((address,int(port)))

        Driver.__init__(self, **kwargs)
    
    def send(self,command):
        self.s.send(command)
    def write(self,query):
        self.s.send((query+'\n').encode())
    def read(self):
        rep = self.s.recv(1000).decode()
        return rep
    def query(self, qry):
        self.write(qry)
        time.sleep(0.2)
        return self.read()
    def close(self):
        self.s.close()
############################## Connections classes ##############################
#################################################################################


class Channel():
    def __init__(self,dev,channel):
        self.channel = int(channel)
        self.dev  = dev
    
    def amplitude(self,amplitude):
        self.dev.write_to_channel(self.channel,f'AMPL {amplitude}')
    def frequency(self,frequency):
        self.dev.write_to_channel(self.channel,f'FREQ {frequency}')
    def offset(self,offset):
        self.dev.write_to_channel(self.channel,f'DCOFFS {offset}')
    
    def set_output(self, state):
        """output on, off, normal or invert""" 
        self.dev.write_to_channel(self.channel,f'OUTPUT {state}')
        
    def load_arb(self, arb_chan):
        """chan: arbitrary channel to load"""
        self.set_mode('ARB')
        self.dev.write_to_channel(self.channel,f'ARBLOAD ARB{arbchan}')
    def write_array_to_byte(self,l,arb_chan):
        """Arguments: array, arbitrary waveform number to address the array to
        Note: ARB1 < BIN > Load data to an existing arbitrary waveform memory location ARB1. The data consists of two bytes per point with no characters between bytes or points. The point data is sent high byte first. The data block has a header which consists of the # character  followed by several ascii coded numeric characters. The first of these defines the number of ascii characters to follow and these following characters define the length of the binary data in bytes. The instrument will wait for data indefinitely If less data is sent. If more data is sent the extra is processed by the command parser which results in a command error."""
        self.set_mode('ARB')
        a = l.astype('<u2').tostring()
        temp = str(2*len(l))
        ARB = str(arb_chan)
        qry = b'ARB'+ bytes(str(ARB),'ascii') +bytes(' #','ascii')+ bytes(str(len(temp)),'ascii')+bytes(temp,'ascii')+a +b' \n'
        self.dev.send(qry)
        time.sleep(0.2)
        
    def set_mode(self,mode_name):
        self.dev.write_to_channel(self.channel,f'WAVE {mode_name}')
        
        
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'amplitude','write':self.amplitude,'type':float,'help':"set the amplitude"})
        model.append({'element':'variable','name':'offset','write':self.offset,'type':float,'help':"Set the offset"})
        model.append({'element':'variable','name':'frequency','write':self.frequency,'type':float,'help':"Set the frequency"})
        model.append({'element':'variable','name':'output','write':self.set_output,'type':str,'help':"Enable/disable the output. Accepted arguments are: ON, OFF"})
        model.append({'element':'variable','name':'set_mode','write':self.set_mode,'type':str,'help':"Set the output mode. Accepted arguments are: SINE, SQUARE, RAMP, TRIANG, PULSE, NOISE, PRBSPN7, PRBSPN9, PRBSPN11, PRBSPN15, PRBSPN20, PRBSPN23, PRBSPN29, PRBSPN31, ARB"})
        return model
