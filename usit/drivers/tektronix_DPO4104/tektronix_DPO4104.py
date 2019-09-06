#!/usr/bin/env python3

import vxi11 as v
from optparse import OptionParser
import sys,os
import subprocess
import time

ADDRESS = '169.254.172.5'

class Device():
    def __init__(self,channel=None,address=ADDRESS,filename=None,query=None,command=None,measure=None,PRINT=False):
        self.scope = v.Instrument(address)

        if query:
            print('\nAnswer to query:',query)
            self.scope.write(query)
            rep = self.scope.read()
            print(rep,'\n')
            sys.exit()
        elif command:
            print('\nExecuting command',command)
            self.scope.write(command)
            print('\n')
            sys.exit()
                            
        self.scope.write('HORizontal:RECOrdlength?')
        length = self.scope.read()
        self.scope.write('DAT:STAR 1')
        self.scope.write('DAT:STOP '+str(length))
        
        if measure:
            for i in range(measure[0]):
                self.scope.write('FPAnel:PRESS RUnstop')
                for k in range(len(channel)):
                    self.get_data(chan=channel[k],filename=str(i),SAVE=True)
                self.scope.write('FPAnel:PRESS RUnstop')
                print('Index of the measurement:',i, '   sleeping for ',measure[1])
                time.sleep(measure[1])
            sys.exit()
            
        if filename:
            self.scope.write('FPAnel:PRESS RUnstop')
            for i in range(len(channel)):
                self.scope.write('DAT:SOU '+channel[i])
                print('trying to get channel',channel[i])
                self.get_data(chan=channel[i],filename=filename,SAVE=True)
        else:
            print('If you want to save, provide an output file name')
        
        self.scope.write('FPAnel:PRESS RUnstop')
        

    def get_data(self,chan='CH1',filename='test_save_file_',PLOT=False,SAVE=False,LOG=True):
        self.scope.write('DAT:ENC FAS')
        #self.scope.write('WFMO:BYT_Nr 1')
        self.scope.write('CURV?')
        self.data = self.scope.read_raw()
        
        self.data = self.data[:-1]     # to remove last shitty point

        ### TO SAVE ###
        if SAVE:
            temp_filename = filename + '_DPO4104' + chan
            temp = os.listdir()                           # if file exist => exit
            for i in range(len(temp)):
                if temp[i] == temp_filename:
                    print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
                    sys.exit()
            
            f = open(temp_filename,'wb')                   # Save data
            f.write(self.data)
            f.close()
            if LOG:
                self.preamb = self.get_log_data()             # Save scope configuration
                f = open(temp_filename + '.log','w')
                f.write(self.preamb)
                f.close()
            print(chan + ' saved')
    
    def get_log_data(self):
        self.scope.write('WFMO?')
        return self.scope.read()          
    
    def stop(self):
        pass
    def run(self):
        pass
            
if __name__ == '__main__':

    usage = """usage: %prog [options] arg
    
               WARNING: - Make sure all the channel you provide are active
               
               EXAMPLES:
                   DPO4104 1 -o filename
               Record the first channel and create two files name filename_DPO4104CH1 and filename_DPO4104CH1.log


               Work TODO: - write a self.run and a self.stop function

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-i", "--address", type="string", dest="address", default=ADDRESS, help="Set IP address to use for the communication" )
    parser.add_option("-m", "--measure", type="string", dest="measure", default=None, help="number of measure to provide as list or tuple: [nbmeas,sleeptime]" )
    (options, args) = parser.parse_args()

    ### Compute channels to acquire ###
    #if (len(args) == 0) and (options.com is not None):
        #DPO_4104(query=options.com)
    if (len(args) == 0) and (options.com is None) and (options.que is None):
        print('\nYou must provide at least one channel\n')
        sys.exit()
    elif len(args) == 1:
        chan = []
        temp_chan = args[0].split(',')                  # Is there a coma?
        for i in range(len(temp_chan)):
            chan.append('CH' + temp_chan[i])
    else:
        chan = []
        for i in range(len(args)):
            chan.append('CH' + str(args[i]))
    print(chan)
    
    ### Start the talker ###
    Device(channel=chan,query=options.que, address=options.address,command=options.com,filename=options.filename,measure=options.measure)
    
