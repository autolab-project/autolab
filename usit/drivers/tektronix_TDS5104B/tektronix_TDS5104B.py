#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import sys,os
import time
from numpy import frombuffer,int8


class Device():
    def __init__(self,nb_channels=4):
              
        self.nb_channels = int(nb_channels)
        
        self.write('HORizontal:RECOrdlength?')
        string = self.read()
        length = string[len(':HORIZONTAL:RECORDLENGTH '):]
        self.write('DAT:STAR 1')
        self.write('DAT:STOP '+length)
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))
        
    
    ### User utilities
    def get_data_channels(self,channels=[]):
        """Get all channels or the ones specified"""
        self.stop()
        while not self.is_stopped():time.sleep(0.05)
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels():
            time.sleep(0.1)
            getattr(self,f'channel{i}').get_data_raw()
            getattr(self,f'channel{i}').get_log_data()
        self.run()
        
    def save_data_channels(self,filename,channels=[],FORCE=False):
        if channels == []: channels = list(range(1,self.nb_channels+1))
        for i in channels():
            getattr(self,f'channel{i}').save_data_raw(filename=filename,FORCE=FORCE)
            getattr(self,f'channel{i}').save_log_data(filename=filename,FORCE=FORCE)
        
    ### Trigger functions
    def run(self):
        self.scope.write('ACQUIRE:STATE ON')
    def stop(self):
        self.scope.write('ACQUIRE:STATE OFF')
    def is_stopped(self):
        return '0' in self.query('ACQUIRE:STATE?')


#################################################################################
############################## Connections classes ##############################
class Device_VXI11(Device):
    def __init__(self, address='192.168.0.8', **kwargs):
        import vxi11 as v
    
        self.inst = v.Instrument(address)
        Device.__init__(self, **kwargs)

    def query(self, command, nbytes=100000000):
        self.write(command)
        return self.read(nbytes)
    def read_raw(self):
        self.inst.read_raw()
    def read(self,nbytes=100000000):
        self.inst.read(nbytes)
    def write(self,cmd):
        self.inst.write(cmd)
    def close(self):
        self.inst.close()
############################## Connections classes ##############################
#################################################################################


class Channel():
    def __init__(self,dev,channel):
        self.channel = int(channel)
        self.dev  = dev
        self.autoscale = False
    
    
    def get_data_raw(self):
        self.dev.write(f'DAT:SOU CH{self.channel}')
        self.dev.write('DAT:ENC FAS')
        self.dev.write('WFMO:BYT_Nr 1')
        self.dev.write('CURV?')
        self.data_raw = self.dev.read_raw()
        self.data_raw = self.data_raw[7:-1]
        return self.data_raw
    def get_log_data(self):
        self.dev.write(f'DAT:SOU CH{self.channel}')
        self.dev.write('WFMO?')
        self.log_data = self.dev.read()
        return self.log_data     
    def get_data(self):
        return frombuffer(self.get_data_raw(),int8)
        
    def save_data_raw(self,filename,FORCE=False):
        temp_filename = f'{filename}_TDS5104BCH{self.channel}'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        f = open(temp_filename,'wb')# Save data
        f.write(self.data_raw)
        f.close()
    def save_log_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_TDS5104BCH{self.channel}.log'
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


if __name__ == '__main__':
    from optparse import OptionParser
    import inspect
    
    usage = """usage: %prog [options] arg
    
                EXAMPLES:
                    get_TDS5104B -o filename 1,3
                Records the temporal traces of both channel 1 and 3. Each of them are saved in two different files: 1 composed of int8 and 1 (.log) composed of all the values necessary to retrieve initial values in Volts.

                Datas are recorded in int8 format
               
                Headers contains:
                :WFMOUTPRE:BYT_NR 2;BIT_NR 16;ENCDG ASCII;BN_FMT RI;BYT_OR
                MSB;WFID 'Ch1, DC coupling, 100.0mV/div, 4.000us/div, 10000
                points, Sample mode';NR_PT 10000;PT_FMT Y;XUNIT 's';XINCR
                4.0000E-9;XZERO - 20.0000E-6;PT_OFF 0;YUNIT 'V';YMULT
                15.6250E-6;YOFF :”6.4000E+3;YZERO 0.0000
               
               To retrieve real value:
               value_in_units = ((curve_in_dl - YOFf_in_dl) * YMUlt) + YZEro_in_units
               
               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-i", "--address", type="string", dest="address", default='192.168.0.4', help="Set ip address." )
    parser.add_option("-l", "--link", type="string", dest="link", default='VXI11', help="Set the connection type." )
    parser.add_option("-F", "--force",action = "store_true", dest="force", default=None, help="Allows overwriting file" )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    (options, args) = parser.parse_args()
    
    ### Compute channels to acquire ###
    if (len(args) == 0) and (options.com is None) and (options.que is None):
        print('\nYou must provide at least one channel\n')
        sys.exit()
    else:
        chan = [int(a) for a in args[0].split(',')]
    ####################################
    
    ### Start the talker ###
    classes = [name for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass) if obj.__module__ is __name__]
    assert 'Device_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Device_')])
    Device_LINK = getattr(sys.modules[__name__],'Device_'+options.link)
    I = Device_LINK(address=options.address)
    
    if query:
        print('\nAnswer to query:',query)
        rep = I.query(query)
        print(rep,'\n')
        sys.exit()
    elif command:
        print('\nExecuting command',command)
        I.write(command)
        print('\n')
        sys.exit()
        
    ### Acquire ###
    if options.filename:
        I.get_data_channels(channels=chan)
        I.save_data_channels(channels=chan,filename=options.filename,FORCE=options.force)
    
    print('Measurment time', time.time() - t)
    
    I.close()
    sys.exit()
