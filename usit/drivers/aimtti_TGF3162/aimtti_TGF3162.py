#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import socket
from optparse import OptionParser
import sys
import time
from numpy import zeros,ones,linspace,arange,array,copy,concatenate


class Device():
    
    categories = ['Function generator']
    
    def __init__(self,address='169.254.62.40',port=9221):

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((address,port))
        
        
    def amplitude(self,amplitude):
        self.write('AMPL '+amplitude)
    def frequency(self,frequency):
        self.write('FREQ '+frequency)
    def offset(self,offset):
        self.write('DCOFFS '+offset)
    
    def set_output(self, state):
        """output on, off, normal or invert""" 
        self.write('OUTPUT '+ state)
    def load_arb(self, chan):
        """chan: arbitrary channel to load"""
        self.write('WAVE ARB')
        self.write('ARBLOAD ARB'+chan)
    def swap_channel(self,chan):
        """chan is either 1 or 2"""
        self.write('CHN '+chan)
    def write_array_to_byte(self,l,ARB):
        """Arguments: array, arbitrary waveform number to address the array to
        Note: ARB1 < BIN > Load data to an existing arbitrary waveform memory location ARB1. The data consists of two bytes per point with no characters between bytes or points. The point data is sent high byte first. The data block has a header which consists of the # character  followed by several ascii coded numeric characters. The first of these defines the number of ascii characters to follow and these following characters define the length of the binary data in bytes. The instrument will wait for data indefinitely If less data is sent. If more data is sent the extra is processed by the command parser which results in a command error."""
        a = l.astype('<u2').tostring()
        temp = str(2*len(l))
        ARB = str(ARB)
        qry = b'ARB'+ bytes(str(ARB),'ascii') +bytes(' #','ascii')+ bytes(str(len(temp)),'ascii')+bytes(temp,'ascii')+a +b' \n'
        self.s.send(qry)
        time.sleep(0.2)
    
    def write(self,query):
        self.s.send((query+'\n').encode())
    def read(self):
        rep = self.s.recv(1000).decode()
        return rep
    def query(self, qry):
        self.write(qry)
        time.sleep(0.2)
        return self.read()
    def idn(self):
        self.query('*IDN?')
    def close(self):
        pass
        
            
if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_TTITGF3162 -f 80000000 -a 2
                   set_TTITGF3162 -f 80e6 -a 2
                   Note that both lines are equivalent
                   
                   Set the frequency to 80MHz and the power to 2Vpp.
                   
                   Note: Arbitrary waveform available only using a python terminal (for now)
                   
               """
               
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-o", "--offset", type="str", dest="off", default=None, help="Set the offset value." )
    parser.add_option("-a", "--amplitude", type="str", dest="amp", default=None, help="Set the amplitude." )
    parser.add_option("-f", "--frequency", type="str", dest="freq", default=None, help="Set the frequency." )
    parser.add_option("-i", "--address", type="str", dest="address", default='169.254.62.40', help="Set the Ip address to use for communicate." )
    parser.add_option("-p", "--port", type="float", dest="port", default=9221, help="Set the port to use for communicate." )
    (options, args) = parser.parse_args()
    
        ### Compute channels to acquire ###
    if (len(args) != 1) and (options.com is None) and (options.que is None):
        print('\nYou must provide only one channel\n')
        sys.exit()
    elif len(args) == 1:
        chan = []
        temp_chan = args[0].split(',')                  # Is there a coma?
        for i in range(len(temp_chan)):
            chan.append('CHN' + temp_chan[i])
    else:
        print('\nYou must provide only one channel\n')
        sys.exit()
    print(chan)
    ### Start the talker ###
    I = Device(address=options.address)
    
    if options.query:
        print('\nAnswer to query:',options.query)
        I.write(options.query)
        rep = I.read()
        print(rep,'\n')
        sys.exit()
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
        sys.exit()
    if chan:
        I.swap_channel(chan)
    if options.amplitude:
        I.amplitude(options.amplitude)
    if options.frequency:
        I.frequency(options.frequency)
    if options.offset:
        I.offset(options.offset)
    
    I.close()
    sys.exit()
