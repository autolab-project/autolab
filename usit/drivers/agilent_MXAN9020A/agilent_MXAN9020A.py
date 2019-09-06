#!/usr/bin/env python3
import vxi11 as vxi
import sys,os
import time
from optparse import OptionParser
import subprocess
from numpy import savetxt,linspace

ADDRESS="169.254.124.188"

class Device():
    def __init__(self,address=ADDRESS):
        ### Establish the connection ###
        self.sock = vxi.Instrument(address)
        
        
    def get_data(self):
        self.data  = eval(self.query("TRAC:DATA? TRACE1"))
        start = eval(self.query("SENS:FREQ:START?"))
        stop  = eval(self.query("SENS:FREQ:STOP?"))
        self.lambd = linspace(start,stop,len(data))
        
    def save_data(self,filename,FORCE=None):
        temp_filename = filename + '_MXAN9020A.txt'
        temp = os.listdir()                           # if file exist => exit
        for i in range(len(temp)):
            if temp[i] == temp_filename and not(FORCE):
                print('\nFile ', temp_filename, ' already exists, change filename, remove old file or use -F option to overwrite\n')
                sys.exit()

        savetxt(temp_filename,(self.lambd,self.amp))
    
    def single(self):
        self.write('*TRG')
    
    def write(self, msg):
        self.sock.write(msg)
    def read(self):
        msg=self.sock.read()
        return msg
    def query(self,msg,length=2048):
        """Sends question and returns answer"""
        self.write(msg)
        return(self.read())
    def close(self):
        pass

if __name__=="__main__":
    usage = """usage: %prog [options] arg

               EXAMPLES:
                   get_MXA9020A -o filename
               Record the spectrum and create one file with two columns lambda,spectral amplitude

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-F", "--force", type="string", dest="force", default=None, help="Allows overwriting file" )
    parser.add_option("-i", "--address", type="string", dest="address", default=ADDRESS, help="Set the ip address to establish the communication with" )
    parser.add_option("-t", "--trigger", action = "store_true", dest ="trigger", default=False, help="Make sure the instrument trigger once and finishes sweeping before acquiring the data")
    (options, args) = parser.parse_args()

    
    I = Device(address=options.address)

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
    
    I.prev_state = I.query('INIT:CONT?')
    if options.trigger:
        I.single()
    I.query('INIT:CONT OFF;*OPC?')
    
    if options.filename:
        I.get_data()
        ### TO SAVE ###
        I.save_data(options.filename,FORCE=options.force)
    
    I.write('INIT:CONT '+I.prev_state)
    
    I.close()
    sys.exit()
