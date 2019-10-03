#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    category = 'Function generator'
    
    def __init__(self,nb_channels=4):
        
        self.nb_channels = int(nb_channels)
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))
    
    
    def write_to_channel(self,channel,command):
        self.write(f'SETUPCH {channel}')
        self.write(command)
        
        
    def idn(self):
        self.write('*IDN?\r\n')


#################################################################################
############################## Connections classes ##############################
class Driver_USB(Driver):
    def __init__(self, **kwargs):
        import usb
        import usb.core
        import usb.util
        
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
        rm        = v.ResourceManager()
        self.inst = rm.get_instrument(address)
        
        Driver.__init__(self, **kwargs)
        
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
        
############################## Connections classes ##############################
#################################################################################


class Channel():
    def __init__(self,dev,channel):
        self.channel = int(channel)
        self.dev     = dev

    def amplitude(self,val):
        """ Change amplitude in Vpp """
        self.dev.write_to_channel(self.channel,f'AMPL {val}')
    def frequency(self,val):
        """ Change the frequency in Hz """
        self.dev.write_to_channel(self.channel,f'WAVFREQ {val}')
    def period(self,val):
        """ Change the period in s """
        self.dev.write_to_channel(self.channel,f'WAVPER {val}')



if __name__ == '__main__':
    from optparse import OptionParser
    import inspect
    import sys

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
    I = Driver()
    
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
