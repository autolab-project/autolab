#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- Wavemaster 8620A
- Waverunner 104Xi
- Waverunner 6050A
"""

import sys,os
import time
from numpy import int8,int16,frombuffer
import numpy as np


class Device():
    def __init__(self,nb_channels=4):
        
        self.nb_channels = int(nb_channels)
        self.encoding    = 'BYTE'
        
        self.write('CFMT DEF9,'+self.encoding+',BIN')
        self.write('CHDR SHORT')
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))
    
    
    ### User utilities
    def acquire_data_channels(self,channels=[]):
        """Get all channels or the ones specified"""
        previous_trigger_state = self.get_previous_trigger_state()    #1 WARNING previous trigger state in memory or returned
        self.stop()
        self.is_stopped()
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels():
            if not(getattr(self,f'channel{i}').is_active()): continue
            getattr(self,f'channel{i}').get_data_raw()
            getattr(self,f'channel{i}').get_log_data()
        self.set_previous_trigger_state(previous_trigger_state)
        
    def save_data_channels(self,filename,channels=[],FORCE=False):
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in self.active_channels():
            getattr(self,f'channel{i}').save_data(filename=filename,FORCE=FORCE)
            getattr(self,f'channel{i}').save_log_data(filename=filename,FORCE=FORCE)
        
    ### Trigger functions
    def single(self):
        self.inst.write("TRMD SINGLE")
    def stop(self):
        self.inst.write("TRMD STOP")
    def is_stopped(self):
        while self.query('TRMD?') != 'TRMD STOP':
            time.sleep(0.05)
        return True
    def get_previous_trigger_state(self):
        return self.query('TRMD?')
        
    def set_previous_trigger_state(self):                 # go to 1 WARNING
        self.scope.write(self.prev_trigg_mode)
        
    ### Cross-channel settings 
    def set_encoding(self,encoding):
        self.encoding = encoding
        self.scope.write('CFMT DEF9,'+self.encoding+',BIN')
        if encoding=='BYTE':dtype=int8;NUM=256;LIM=217          # 15% less than the maximal number possible
        elif encoding=='WORD':dtype=int16;NUM=65536;LIM=55700   # 15% less than the maximal number possible
    def get_encoding(self):
        return self.encoding
  
    def getDriverConfig(self):
        
        config = []
        for num in range(1,self.nb_channels+1) :
            config.append({'element':'module','name':f'channel{num}','object':getattr(self,f'channel{num}')})
        return config
    
#################################################################################
############################## Connections classes ##############################
class Device_TCPIP(Device):
    def __init__(self, address=None, **kwargs):
        import visa as v
        
        rm        = v.ResourceManager()
        self.inst = rm.get_instrument(address)
        Device.__init__(self, **kwargs)
    
    def query(self,command):
        self.write(command)
        return self.read()
    def read(self):
        return self.inst.read()
    def read_raw(self):
        return self.inst.read_raw()
    def write(self,command):
        self.inst.write(command)
    def close(self):
        self.inst.close()

class Device_VXI11(Device):
    def __init__(self, address=None, **kwargs):
        import vxi11 as v
    
        self.inst = v.Instrument(address)
        Device.__init__(self, **kwargs)

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
        self.autoscale_iter   = 0
        self.autoscale_factor = 8
    
    
    def get_data_raw(self):
        if self.autoscale_iter:
            self.do_autoscale()
        self.dev.write(f'C{self.channel}:WF? DAT1')
        self.data = self.dev.read_raw()
        self.data = self.data[self.data.find(b'#')+11:-1]
        return self.data
                                             
    def get_data(self):
        return frombuffer(self.get_data_raw(),int8)
                                             
    def get_log_data(self):
        self.log_data = self.dev.query(f"C{self.channel}:INSP? 'WAVEDESC'")
        return self.log_data
    
    
    def save_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_lecroyC{self.channel}'
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
        k = 1
        while k <= self.autoscale_iter():
            mi = self.get_min()
            ma = self.get_max()
            diff = abs(mi) + abs(ma)
            
            val = round((-1)*diff/2. + abs(mi),3)
            self.set_vertical_offset(val)
            new_channel_amp  = round(diff/self.autoscale_factor,3)
            if new_channel_amp<0.005: new_channel_amp = 0.005 # if lower than the lowest possible 5mV/div
            self.set_vertical_scale(new_channel_amp)
            
            self.single()
            print('Optimisation loop index:', k,self.autoscale_iter)
            if k==self.autoscale_iter:
                VDIV = self.get_vertical_scale()
                OFST = self.get_vertical_offset()
                R_MI = -(4.5 * VDIV) - OFST
                R_MA =   4.5 * VDIV  - OFST
                mi = self.get_min()
                ma = self.get_max()
                if mi<R_MI or ma>R_MA:                        #if trace out of the screen optimize again
                    print('(SCOPE)   Min:',R_MI,' Max:',R_MA)
                    print('(TRACE)   Min:',mi,' Max:',ma)
                    k = k-1
            k = k+1
            
    def set_autoscale_iter(self,val):
        self.autoscale_iter = val
    def get_autoscale_iter(self):
        return self.autoscale_iter
    def set_autoscale_factor(self,val):
        self.autoscale_factor = val
    def get_autoscale_factor(self):
        return self.autoscale_factor
           
    def is_active(self):
        temp = self.dev.query(f'C{self.channel}:TRA?')
        return 'ON' in temp



    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'min','type':float,'unit':'V','read':self.get_min,'help':'Get minimum value of the current signal'})
        config.append({'element':'variable','name':'max','type':float,'unit':'V','read':self.get_max,'help':'Get maximum value of the current signal'})
        config.append({'element':'variable','name':'mean','type':float,'unit':'V','read':self.get_mean,'help':'Get mean value of the current signal'})
        config.append({'element':'variable','name':'trace_raw','type':bytes,'read':self.get_data_raw,'help':'Get the current trace in bytes'})
        config.append({'element':'variable','name':'trace','type':np.ndarray,'read':self.get_data,'help':'Get the current trace in numpy'})
        config.append({'element':'variable','name':'verticalScale','type':float,'unit':'V/div','read':self.get_vertical_scale,'write':self.set_vertical_scale,'help':'Set the vertical scale of the channel'})
        config.append({'element':'variable','name':'verticalOffset','type':float,'unit':'V','read':self.get_vertical_offset,'write':self.set_vertical_offset,'help':'Set the vertical offset of the channel'})
        return config

if __name__ == '__main__':
    
    a = Device_VXI11("192.168.0.18")
#    from optparse import OptionParser
#    import inspect
#    
#    usage = """usage: %prog [options] arg
#
#               EXAMPLES:
#                   get_lecroywavemaster 1 -o filename
#                   Record the first channel and create two files name filename_lecroy and filename_lecroy.log
#            
#                   get_lecroywavemaster -i 192.168.0.4 -e WORD -o test 3
#                   Same as before but record channel 3 with giving an IP address and an int16 data type
#                    
#                   get_lecroywavemaster -i 192.168.0.5 -F -t -m [10,1,2] -n 8 -o test 1,2
#                   Uses autoscale for automatic adjustments of the vertical scale on channel 1 and 2
#                   Note: if channel is not to be acquired it won't be subjected to amplitude optimization
#                    
#               
#               IMPORTANT INFORMATIONS:
#                    - Datas are obtained in a binary format: int8 
#                    - To retrieve datas (in "VERTUNIT"), see corresponding log file:
#                    DATA(VERTUNIT) = DATA(ACQUIRED) * VERTICAL_GAIN - VERTICAL_OFFSET
#                    
#                See for more informations:  toniq/Prog_guide/Lecroy.pdf
#
#               """
#    parser = OptionParser(usage)
#    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
#    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
#    parser.add_option("-i", "--address", type="string", dest="address", default='192.168.0.18', help="Set ip address." )
#    parser.add_option("-l", "--link", type="string", dest="link", default='VXI11', help="Set the connection type." )
#    parser.add_option("-F", "--force",action = "store_true", dest="force", default=None, help="Allows overwriting file" )
#    parser.add_option("-e", "--encoding", type="string", dest="encoding", default='BYTE', help="For mofifying the encoding format of the answer" )
#    parser.add_option("-m", "--spe_mode", type="string", dest="spe_mode", default=None, help="For allowing auto modification of the vertical gain. List of: spe_mode iteration number, all the channels to apply spe mode to. Note if no channel specified, all the channel are corrected. WARNING: if you want all the channels to correpond to the same trigger event, you need to spe_mode one channel only and to physically plug the cable in the first channel acquired (first in the list 1->4)")
#    parser.add_option("-n", "--spe_fact", type="float", dest="spe_fact", default=8., help="For setting limits of the vertical gain, units are in number of scope divisions here. WARNING: Do not overpass 9 due to a security in the code! WARNING: the number of vertical divisions might depend on the scope (8 or 10 usually)." )
#    parser.add_option("-t", "--trigger", action="store_true", dest="trigger", default=False, help="Ask the scope to trigger once before acquiring." )
#    (options, args) = parser.parse_args()
#    
#    ### Compute channels to acquire ###
#    if (len(args) == 0) and (options.com is None) and (options.que is None):
#        print('\nYou must provide at least one channel\n')
#        sys.exit()
#    else:
#        chan = [int(a) for a in args[0].split(',')]
#    ####################################
#    
#    ### Start the talker ###
#    classes = [name for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass) if obj.__module__ is __name__]
#    assert 'Device_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Device_')])
#    Device_LINK = getattr(sys.modules[__name__],'Device_'+options.link)
#    I = Device_LINK(address=options.address)
#    
#    if query:
#        print('\nAnswer to query:',query)
#        rep = I.query(query)
#        print(rep,'\n')
#        sys.exit()
#    elif command:
#        print('\nExecuting command',command)
#        I.write(command)
#        print('\n')
#        sys.exit()
