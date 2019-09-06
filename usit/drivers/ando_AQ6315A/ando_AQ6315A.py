#!/usr/bin/env python3

from optparse import OptionParser
import sys,os
import time
import numpy as np
import visa as v
import subprocess
from numpy import savetxt,linspace

ADDRESS = 'GPIB::3::INSTR'

class Device():
    def __init__(self,address=ADDRESS):
        ### establish GPIB communication ###
        r          = v.ResourceManager()
        self.scope = r.get_instrument(address)
        

    def save_data(self,filename,FORCE=None):
        temp_filename = filename + '_ANDOAQ6315A'
        temp = os.listdir()              # if file exist => exit
        for i in range(len(temp)):
            if temp[i] == temp_filename and not(FORCE):
                print('\nFile ', temp_filename, ' already exists, change filename, remove old file or use -F option to overwrite\n')
                sys.exit()
        savetxt(temp_filename,(self.lambd,self.amp))
            
    def get_data(self):
        print("ACQUIRING...")
        self.amp    = self.query("LDATA").split(',')[1:]
        self.amp    = [eval(self.amp[i]) for i in range(len(self.amp))]
        stopWL     = float(self.query("STPWL?"))
        startWL    = float(self.query("STAWL?"))
        self.lambd = linspace(startWL,stopWL,len(self.amp))
    
    def set_start_wavelength(self,value):
        scope.write('STAWL '+value)
    def set_stop_wavelength(self,value):
        scope.write('STPWL '+value)
        
    def singleSweep(self):
        s = self.write("SGL")
        return s
    def repeatSweep(self):
        scope.write('RPT')
    
    def query(self,query,length=1000000):
        self.write(query)
        r = self.read(length=length)
        return r
    def write(self,query):
        self.string = query + '\n'
        self.scope.write(self.string)
    def read(self,length=10000000):
        rep = self.scope.read_raw()
        return rep
        
    def close(self):
        pass

if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               
               EXAMPLES:
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-q", "--query", type="str", dest="com", default=None, help="Set the query to use." )
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to execute." )
    parser.add_option("-i", "--address", type="str", dest="address", default=ADDRESS, help="Set the gpib port to use." )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-F", "--force", type="string", dest="force", default=None, help="Allows overwriting file" )
    (options, args) = parser.parse_args()

    ### Start the talker ###
    I = Device(address=options.address)

    if options.query:                                         # to execute command from outside
        print('\nAnswer to query:',options.query)
        I.write(options.query+'\n')
        rep = I.read()
        print(rep,'\n')
        sys.exit()
    elif options.command:
        print('\nExecuting command',options.command)
        I.scope.write(options.command)
        print('\n')
        sys.exit()
        
    if filename:
        I.get_data()
        I.save_data(filename=options.filename,FORCE=options.force)
    
    I.close()
    sys.exit()
