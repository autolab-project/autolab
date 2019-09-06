#!/usr/bin/env python3

import vxi11 as v
from optparse import OptionParser
import sys
import time
from numpy import fromstring,int8,int16,float64,sign

ADDRESS = '169.254.166.210'

conv = ['T0','T1','A','B','C','D','E','F','G','H']
conv2 = ['T0','AB','CD','EF','GH']

class Device():
    def __init__(self,address=ADDRESS):
        ### Initiate communication ###
        self.inst = v.Instrument(address)


    def get_frequency(self):
        return self.query('TRAT?')
    
    def amplitude(self,channel,amplitude):
        self.write('LAMP'+str(conv2.index(channel))+','+amplitude)
    def frequency(self,frequency):
        self.write('TRAT'+frequency)
    def polarity(self,channel,polarity):
        self.write('LPOL'+str(conv2.index(channel))+','+polarity)
    def offset(self,channel,offset):
        self.write('LOFF'+str(conv2.index(channel))+','+offset)
    def display(self,channel):
        if (channel == []):
            for chan in conv2[1:5]:
                self.ch_disp(chan)
        else: 
            self.ch_disp(channel)
            
    ### PRINT OUT CODE 
    def ch_disp(self,channel):
        ch1 = str(conv.index(channel[0]))
        tmpdelay = self.query('DLAY?'+ch1)
        tmpdelay = tmpdelay.split(',')
    
        if len(channel) == 2:
            ch = str(conv2.index(channel))
            ch2 = str(conv.index(channel[1]))
            
            tmpdelay2 = self.query('DLAY?'+ch2)
            tmpdelay2 = tmpdelay2.split(',')
        
            print('==========CH:'+channel+'==============')
            print('Level Amplitude  :  '+self.query('LAMP?'+ch)+' V')
            print('Level Offset     :  '+self.query('LOFF?'+ch)+' V')
            print('Level Polarity   :  '+self.query('LPOL?'+ch)+'\n')
            print('Delay           '+channel[0]+':  '+ conv[int(tmpdelay[0])]+tmpdelay[1]+' s')
            print('Delay           '+channel[1]+':  '+ conv[int(tmpdelay2[0])]+tmpdelay2[1]+' s\n' )
        else:
            print('==========CH:'+channel+'==============')
            print('Delay           '+channel+':  '+ conv[int(tmpdelay[0])]+tmpdelay[1]+' s\n' )
    
    #Channel delay code block 
    def ad_delay(self, channel, delay):
        if len(channel) == 2:
            ch1 = str(conv.index(channel[0]))
            ch2 = str(conv.index(channel[1]))
        else:
            ch1 = '0'
            ch2 = str(conv.index(channel))
            
        self.write('DLAY'+ch2+','+ch1+','+delay,)
            
    ### BASIC FUNCTIONS
    def query(self, cmd, nbytes=1000000):
        """Send command 'cmd' and read 'nbytes' bytes as answer."""
        self.write(cmd+'\n')
        r = self.read(nbytes)
        return r
    def read(self,nbytes=1000000):
        return self.inst.read(nbytes)
    def write(self,cmd):
        self.inst.write(cmd)
    def close(self):
        self.inst.close()

        
if __name__ == '__main__':

    usage = """usage: %prog [options] arg

               EXAMPLES:
                  offset change : DG645 AB -o 3     3v level offset on AB
                  delay change : DG645 AB -d 10e-6 
                  delay wrt t0 : DG645 A -d 10e-6
                  trigger      : DG645 -f 1000000    
                  polarity     : DG645 AB -p 1  / DG645 AB -p 0
               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="command", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="query", default=None, help="Set the query to use." )
    parser.add_option("-d", "--delay", type="str", dest="delay", default=None, help="Set the delay (s)")
    parser.add_option("-x", "--display", action = "store_true", dest ="display", default=False, help="disp")
    parser.add_option("-a", "--amplitude", type="str", dest="amplitude", default=None, help="Set the amplitude (V)")
    parser.add_option("-f", "--frequency", type="str", dest="frequency", default=None, help="Set the frequency (Hz)")
    parser.add_option("-p", "--polarity", type="str", dest="polarity", default=None, help="Set the level polarity if 1, then up if 0, then down")
    parser.add_option("-o", "--offset", type="str", dest="offset", default=None, help="Set the offset")
    parser.add_option("-i", "--address", type="string", dest="address", default=ADDRESS, help="Set ip address" )
    (options, args) = parser.parse_args()

    chan = []
    # Errors for options that do not require a channel input
    # command, query, display, 
    # amplitude, freq, polarity, level

    if (options.amplitude) or (options.delay) or (options.pol) or (options.offset):
        if (len(args) == 0):
            print('\nYou must provide at least one edge\n')
            sys.exit()
        if (options.pol) or (options.amplitude) or (options.offset):
            if (len(args[0])==1):
                print('\nYou must provide a channel')
                sys.exit()
        if (args[0] in conv) or (args[0] in conv2):
            chan = args[0].upper() 
        else:       
            print('\nYou must provide a channel or edge')
            sys.exit()
    if (options.display) and (len(args) !=0):
        if (args[0] in conv) or (args[0] in conv2):
            chan = args[0].upper() 
        else:       
            print('\nYou must provide a channel or edge')
            sys.exit()
    
    
    ### Start the talker ###
    I = Device(address=options.address)
    
    if options.query:
        print('\nAnswer to query:',options.query)
        rep = I.query(options.query)
        print(rep,'\n')
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
        
    if options.delay:
        I.ad_delay(chan, options.delay)
    if options.amplitude:
        I.amplitude(chan, options.amplitude)
    if options.frequency: 
        I.frequency(options.frequency)
    if options.polarity:
        I.polarity(chan,options.polarity)
    if options.offset: 
        I.offset(chan,options.offset)
    if options.display:
        I.display(chan)
    
    sys.exit()
    

