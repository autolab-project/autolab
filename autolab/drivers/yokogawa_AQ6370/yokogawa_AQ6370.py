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
    
    def __init__(self):
        
        for i in ['A','B','C','D','E','F','G']:
            setattr(self,f'trace{i}',Traces(self,i))
            
        
    ### User utilities
    def get_data_traces(self,traces=[],single=None):
        """Get all traces or the ones specified"""
        if single: self.single()
        while not self.is_scope_stopped(): time.sleep(0.05)
        if traces == []: traces = ['A','B','C','D','E','F','G']
        for i in traces:
            #if not(getattr(self,f'trace{i}').is_active()): continue
            getattr(self,f'trace{i}').get_data()
        
    def save_data_traces(self,filename,traces=[],FORCE=False):
        if traces == []: traces = ['A','B','C','D','E','F','G']
        for i in traces:
            getattr(self,f'trace{i}').save_data(filename=filename,FORCE=FORCE)
        
    ### Trigger functions
    def single(self):
        """Trigger a single sweep"""
        self.write('*TRG')
        while not(self.is_scope_stopped()): pass
    def is_scope_stopped(self):
        return '1' in self.query(':STATUS:OPER:COND?')


    def get_driver_model(self):
        model = []
        for i in ['A','B','C','D','E','F','G']:
            model.append({'element':'module','name':f'line{i}','object':getattr(self,f'trace{i}'), 'help':'Traces'})
        model.append({'element':'variable','name':'is_stopped','read':self.is_scope_stopped, 'type':bool,'help':'Query whether scope is stopped'})
        model.append({'element':'action','name':'single','do':self.single,'help':'Set single mode'})
        return model


#################################################################################
############################## Connections classes ##############################
class Driver_SOCKET(Driver):
    def __init__(self, address='192.168.0.9', port=10001, **kwargs):
        import socket
        
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((address, int(port)))
        self.write('OPEN "anonymous"')
        ans = self.read(1024)
        if not ans=='AUTHENTICATE CRAM-MD5.':
            print("problem with authentication")
        self.write(" ")
        ans = self.read(1024)
        if not ans=='ready':
            print("problem with authentication")
        
        Driver.__init__(self)

    def write(self, msg):
        msg=(msg+"\n").encode()
        self.sock.send(msg)
    def read(self, length=100000):
        msg=''
        while not msg.endswith('\r\n'):
            msg=msg+self.sock.recv(length).decode()
        msg = msg[:-2]
        return msg.strip('\r\n')
    def query(self,msg,length=100000):
        """Sends question and returns answer"""
        self.write(msg)
        return(self.read(length))
    def close(self):
        self.sock.close()
############################## Connections classes ##############################
#################################################################################


class Traces():
    def __init__(self,dev,trace):
        self.trace     = str(trace)
        self.dev       = dev
        self.data_dict = {}
        
    def get_data(self):
        self.data        = self.dev.query(f":TRAC:DATA:Y? TR{self.trace}").split(',')
        self.frequencies = self.get_frequencies()
        self.data        = [float(val) for val in self.data]
        self.frequencies = [float(val) for val in self.frequencies]
        return self.frequencies,self.data
    def get_data_dataframe(self):
        frequencies,data              = self.get_data()
        self.data_dict['frequencies'] = self.frequencies
        self.data_dict['amplitude']   = self.data
        return pandas.DataFrame(self.data_dict)
    
    def get_frequencies(self):
        return self.dev.query(f":TRAC:DATA:X? TR{self.trace}").split(',')
    
    def save_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_AQ6370TR{self.trace}.txt'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        
        savetxt(temp_filename,(self.frequencies,self.data))


    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'spectrum','read':self.get_data_dataframe,'type':pandas.DataFrame,'help':'Current spectrum'})
        return model
    

