#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11 as v
import sys,os
import time
from optparse import OptionParser
import subprocess
from numpy import savetxt

ADDRESS="169.254.108.199"

class Device():
    def __init__(self,address=ADDRESS,channel=None,filename=None,query=None,command=None,FORCE=False,SAVE=True):
        ### Establish the connection ###
        self.scope = v.Instrument(address)

        if query:
            print('\nAnswer to query:',query)
            rep = self.query(query)
            print(rep,'\n')
            sys.exit()
        elif command:
            print('\nExecuting command',command)
            self.scope.write(command)
            print('\n')
            sys.exit()
            
        self.stop()
        self.scope.write('HORizontal:RECOrdlength?')
        string = self.scope.read()
        length = string[len(':HORIZONTAL:RECORDLENGTH '):]
        self.scope.write('DAT:STAR 1')
        self.scope.write('DAT:STOP '+length)
            
        if filename:
            for i in range(len(channel)):
                time.sleep(0.1)
                self.get_data(chan=channel[i],filename=filename,SAVE=SAVE)
            
            self.run()
        else:
            print('If you want to save, provide an output file name')

        sys.exit()


    def get_data(self,chan='CH1',filename='test_save_file_',PLOT=False,SAVE=False,LOG=True,RET=False):
        self.scope.write('DAT:ENC FAS')
        self.scope.write('DAT:SOU '+chan)
        self.scope.write('WFMO:BYT_Nr 1')
        self.scope.write('CURV?')
        self.data = self.scope.read_raw()
        
        self.data = self.data[7:-1]     # to remove last shitty point
        ### TO SAVE ###
        if SAVE:
            temp_filename = filename + '_TDS5104B' + chan
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
        if RET:
            return self.data
    
    def get_log_data(self):
        self.scope.write('WFMO?')
        return self.scope.read()          

    def query(self, cmd, nbytes=1000000):
        """Send command 'cmd' and read 'nbytes' bytes as answer."""
        self.scope.write(cmd)
        r = self.scope.read(nbytes)
        return r
    def run(self):
        self.scope.write('ACQUIRE:STATE ON')
    def stop(self):
        self.scope.write('ACQUIRE:STATE OFF')
    def close(self):
        self.scope.close()

if __name__=="__main__":

    usage = u"""usage: %prog [options] arg

                EXAMPLES:
                    get_TDS5104B -o filename
                Record the spectrum and create one file with two columns lambda,spectral amplitude

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
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-i", "--address", type="string", dest="address", default=ADDRESS, help="Set the IP address to use for the communication" )
    parser.add_option("-F", "--force", type="string", dest="force", default=None, help="Allows overwriting file" )
    (options, args) = parser.parse_args()

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
    
    Device(address=options.address,channel=chan,query=options.que,command=options.com,filename=options.filename,FORCE=options.force)

