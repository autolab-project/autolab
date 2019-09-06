#!/usr/bin/env python3

import usb
import usb.core
import usb.util
from optparse import OptionParser
import sys

class Device():
    def __init__(self):

        dev = usb.core.find(idVendor=0x103e,idProduct=0x03f2)
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
    
    
    def amplitude(self,command):
        """ Change amplitude in Vpp """
        command = 'AMPL ' + command
        self.write(command)
    def frequency(self,command):
        """ Change the frequency in Hz """
        command = 'WAVFREQ ' + command
        self.write(command)
    def period(self,command):
        """ Change the period in s """
        command = 'WAVPER ' + command
        self.write(command)
        
    def init_karen_meas(self):
        """ setup the function generator for karen measurment """
        self.write('SETUPCH 1')
        self.write('ARB PZTRAMP')
        self.amplitude(str(2))           # 2 Vpp
        self.period(str(0.01))            # 10 ms
        self.write('OUTPUT ON')
        
    def close(self):
        self.write('LOCAL')
        pass
    def write(self,query):
        self.string = query + '\r\n'
        self.ep_out.write(self.string)
    def read(self):
        rep = self.ep_in.read(2000000)
        const = ''.join(chr(i) for i in rep)
        const = const#[:const.find('\r\n')]
        return const
    def idn(self):
        self.ep_out.write('*IDN?\r\n')
        

if __name__ == '__main__':
    usage = """usage: %prog [options] arg
               
               
               EXAMPLES:
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-k", "--karen", type="str", dest="kar", default=None, help="Set ON karen's measurment." )
    parser.add_option("-a", "--amplitude", type="str", dest="amp", default=None, help="Set the amplitude." )
    parser.add_option("-f", "--frequency", type="str", dest="freq", default=None, help="Set the frequency." )
    parser.add_option("-p", "--period", type="str", dest="per", default=None, help="Set the period." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    I = Device()
    
    if options.kar:
        I.init_karen_meas()
        sys.exit()
    
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
    
    if options.amplitude:
        I.amplitude(options.amplitude)
    if frequency:
        I.frequency(options.frequency)
    if period:
        I.period(options.period)
    
    I.close()
    sys.exit()
