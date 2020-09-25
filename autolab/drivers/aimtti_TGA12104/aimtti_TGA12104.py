#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    def __init__(self,nb_channels=4):
        
        self.nb_channels = int(nb_channels)
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))
    
    
    def write_to_channel(self,channel,command):
        self.write(f'SETUPCH {channel}')
        self.write(command)
        
        
    def idn(self):
        self.write('*IDN?\r\n')
        return self.read()
        
    def get_driver_model(self):
        model = []
        for num in range(1,self.nb_channels+1) :
            model.append({'element':'module','name':f'channel{num}','object':getattr(self,f'channel{num}')})
        return model

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


    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'amplitude','write':self.amplitude,'type':float,'help':"set the amplitude"})
        model.append({'element':'variable','name':'period','write':self.period,'type':float,'help':"Set the period"})
        model.append({'element':'variable','name':'frequency','write':self.frequency,'type':float,'help':"Set the frequency"})
        return model
