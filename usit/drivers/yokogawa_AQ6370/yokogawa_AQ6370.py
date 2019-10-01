#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import sys,os
import time
from numpy import savetxt,linspace
import pandas

class Device():
    def __init__(self):
        
        for i in ['A','B','C','D','E','F','G']:
            setattr(self,f'trace{i}',Traces(self,i))
    
    ### User utilities
    def get_data_traces(self,traces=[],single=None):
        """Get all traces or the ones specified"""
        if single: self.single()
        self.is_scope_stopped()
        if traces == []: traces = ['A','B','C','D','E','F','G']
        for i in traces():
            if not(getattr(self,f'trace{i}').is_active()): continue
            getattr(self,f'trace{i}').get_data()
        
    def save_data_traces(self,filename,traces=[],FORCE=False):
        if traces == []: traces = ['A','B','C','D','E','F','G']
        for i in traces():
            getattr(self,f'trace{i}').save_data(filename=filename,FORCE=FORCE)
        
    ### Trigger functions
    def single(self):
         """Trigger a single sweep"""
        self.send('*TRG')
    def is_scope_stopped(self):
        flag = 0.1
        while self.query(':STATUS:OPER:COND?') != '1':
            time.sleep(flag)
            flag = flag + 0.1
        

#################################################################################
############################## Connections classes ##############################
class Device_SOCKET(Device):
    def __init__(self, address='192.168.0.9', **kwargs):
        import socket
        
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((address, PORT))
        self.send('OPEN "anonymous"')
        ans = self.recv(1024)
        if not ans=='AUTHENTICATE CRAM-MD5.':
            print("problem with authentication")
            sys.exit(1)
        self.send(" ")
        ans = self.recv(1024)
        if not ans=='ready':
            print("problem with authentication")
            sys.exit(1)
        
        Device.__init__(self, **kwargs)

    def send(self, msg):
        msg=msg+"\n"
        self.sock.send(msg)
    def recv(self, length=2048):
        msg=''
        while not msg.endswith('\r\n'):
            msg=msg+self.sock.recv(length)
        msg = msg[:-2]
        return msg
    def query(self,msg,length=2048):
        """Sends question and returns answer"""
        self.send(msg)
        #time.sleep(1)
        return(self.recv(length))
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
        self.data        = self.dev.query(f":TRAC:DATA:Y? TR{self.trace}", length=100000).split(',')
        self.frequencies = self.get_frequencies()
        return self.frequencies,self.data
    def get_data_dataframe(self):
        frequencies,data              = self.get_data()
        self.data_dict['frequencies'] = self.frequencies
        self.data_dict['amplitude']   = self.data
        return pandas.DataFrame(self.data_dict)
    
    def get_frequencies(self):
        return self.dev.query(f":TRAC:DATA:X? TR{self.trace}", length=1000000).split(',')
    
    def save_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_AQ6370TR{self.trace}.txt'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        
        savetxt(temp_filename,(self.frequencies,self.data))


if __name__ == '__main__':
    from optparse import OptionParser
    import inspect
    
    usage = """usage: %prog [options] arg

               EXAMPLES:
                   get_AQ6370 -o filename A,B,C,D,E,F,G
               Record the spectrum and create one file with two columns lambda,spectral amplitude

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-i", "--address", type="string", dest="address", default='192.168.0.4', help="Set ip address." )
    parser.add_option("-l", "--link", type="string", dest="link", default='SOCKET', help="Set the connection type." )
    parser.add_option("-F", "--force",action = "store_true", dest="force", default=None, help="Allows overwriting file" )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-t", "--trigger", action="store_true", dest="trigger", default=False, help="Ask the scope to trigger once before acquiring." )
    (options, args) = parser.parse_args()
    
    ### Compute traces to acquire ###
    if (len(args) == 0) and (options.com is None) and (options.que is None):
        print('\nYou must provide at least one trace\n')
        sys.exit()
    else:
        chan = [str(a) for a in args[0].split(',') if a in ['A','B','C','D','E','F','G']]
    ####################################
    
    ### Start the talker ###
    classes = [name for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass) if obj.__module__ is __name__]
    assert 'Device_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Device_')])
    Device_LINK = getattr(sys.modules[__name__],'Device_'+options.link)
    I = Device_LINK(address=options.address)
    
    if options.query:
        print('\nAnswer to query:',options.query)
        rep = I.query(options.query)
        print(rep,'\n')
        sys.exit()
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
        sys.exit()
    
    if options.filename:
        I.get_data_traces(traces=chan,single=options.trigger)
        I.save_data_traces(options.filename,FORCE=options.force)

    
    I.close()
    sys.exit()
