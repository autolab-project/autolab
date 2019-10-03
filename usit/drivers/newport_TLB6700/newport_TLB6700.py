#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import usb
import usb.core
import usb.util
from optparse import OptionParser
import sys
import time
import numpy as np

class Device():
    
    categories = ['Optical source']
    
    def __init__(self):
        dev = usb.core.find(idVendor=0x104d,idProduct=0x100a)
        dev.reset()
        dev.set_configuration()

        interface = 0
        if dev.is_kernel_driver_active(interface) is True:
            # tell the kernel to detach
            dev.detach_kernel_driver(interface)
            # claim the device
            usb.util.claim_interface(dev, interface)

        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]
        self.ep_out = usb.util.find_descriptor(intf,custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        self.ep_in = usb.util.find_descriptor(intf,custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)

        assert self.ep_out is not None
        assert self.ep_in is not None
    
            
    def func_scanpiezo(self,scanpiezo):
        if (len(scanpiezo) == 3) or (len(scanpiezo) == 4):
            try:
                SAVE = scanpiezo[3]
            except:
                SAVE = None
            scan_time = float(scanpiezo[2])
            scanpiezo = scanpiezo[:2]
        elif len(scanpiezo)!=2:
            print('Please provide a list of at least 2 values for the scan')
            sys.exit()
        beg,end=[scanpiezo[i] for i in range(len(scanpiezo))]
        ### kernel ###
        step = 1
        end = end+step
        ramp = np.arange(beg,end,step)
        t = time.time();l=[]
        for i in range(len(ramp)):
            self.func_piezo(ramp[i])
            time.sleep(scan_time/len(ramp))
            l.append(time.time()-t)
            print('piezo value: ', ramp[i], '     time passed: ', l[i])
        ### save ###
        if SAVE:
            f = open('time'+str(SAVE),'w')
            f.write(l)
            f.close()
        sys.exit()
    
    def func_piezo(self,piezo):
        """ send the value to set for the piezo to the controller """
        self.write('SOURce:VOLTage:PIEZo '+str(piezo))
        self.read()
        
    def wavelength(self,lambd):
        self.write('SOUR:WAVE '+str(lambd))
        self.write('OUTP:TRAC ON')
        
    def scan_wavelength(self,scan):
        if len(scan) == 3:
            vel = str(scan[2])
            scan = scan[:2]
            self.write('SOUR:WAVE:SLEW:FORW '+vel)                     # value in nm/s
            self.write('SOUR:WAVE:SLEW:RET '+vel)  
        elif len(scan)!=2:
            print('Please provide a list of at least 2 values for the scan')
            sys.exit()
        beg,end=[str(scan[i]) for i in range(len(scan))]
        self.write('SOURce:WAVE:START '+beg)
        self.write('SOURce:WAVE:STOP '+end)
        self.write('OUTPut:SCAN:START')


    def write(self,query):
        self.string = query + '\r\n'
        self.ep_out.write(self.string)
        
    def read(self):
        rep = self.ep_in.read(64)
        const = ''.join(chr(i) for i in rep)
        const = const[:const.find('\r\n')]
        return const

    def idn(self):
        self.ep_out.write('*IDN?\r\n')
        
    def close(self):
        pass
            
        
if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               Think to provide a tuple of values (min,max) for the scans
               
               EXAMPLES:
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--query", type="str", dest="com", default=None, help="Set the query to use." )
    parser.add_option("-w", "--wavelength", type="float", dest="wl", default=None, help="Set the wavelength value." )
    parser.add_option("-s", "--scan", type="string", dest="scan", default=None, help="Set the scan values [min,max,speed]." )
    parser.add_option("-p", "--piezo", type="float", dest="piezo", default=None, help="Set the current to apply to the piezo." )
    parser.add_option("-r", "--scanpiezo", type="string", dest="scanpiezo", default=None, help="Set the values for the piezo scan [min,max,time_scan]." )
    (options, args) = parser.parse_args()
    
    if options.scan:
        options.scan = eval(options.scan)
    if options.scanpiezo:
        options.scanpiezo = eval(options.scanpiezo)
    
    ### Start the talker ###
    I = Device()
    
    if options.query:                          
        print('\nAnswer to query:',options.query)
        I.write(options.query)
        rep = I.read()
        print(rep,'\n')
        sys.exit()
        
    if options.lambd:
        I.wavelength(options.lambd)
    if options.piezo or options.piezo==0:
        I.func_piezo(options.piezo)
    if options.scanpiezo:
        I.func_scanpiezo(options.scanpiezo)
        sys.exit()
    if options.scan:
        I.scan_wavelength(options.scan)
        sys.exit()

        
    I.close()
    sys.exit()
