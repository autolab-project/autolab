#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Function generator'

class Driver_parser():
    def __init__(self, Instance, name,**kwargs):
        self.name     = name
        self.Instance = Instance
        
        
    def add_parser_usage(self,message):
        """Usage to be used by the parser"""
        usage = f"""
{message}

----------------  Examples:  ----------------

usage:    autolab driver [options] args

    autolab driver -D {self.name} -A TCPIP::192.168.0.3::INSTR -C VISA -a 1 -o 1 -f 50KHZ -c 1,2
    set the frequency to 50 kHz, the amplitude to 1V, the offset to 1V for both channel 1 and 2

    autolab driver -D nickname -p w10NS 1
    set pulse mode to channel 1 with pulse width of 10NS (see below -p option help for further assistance), using the device nickname as defined in local_config.ini

    autolab driver -D nickname -p d10 2
    set pulse mode to channel 2 with duty cycle of 10 percent, using the device nickname as defined in local_config.ini
            """
        return usage
        
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-o", "--offset", type=str, dest="offset", default=None, help="Set the offset value in Volts." )
        parser.add_argument("-d", "--dc_mode", type=str, dest="dc_mode", default=None, help="Set dc mode on and set offset." )
        parser.add_argument("-p", "--pulsemode", type=str, dest="pulsemode", default=None, help="Set pulse mode and use argument as either the duty cycle or the pulse width depending on the first letter 'd' or 'w' (see examples). The duty cycle unit is percent. The pulse width unit is second; you may specify it as 'w10MS'(for microseconds) 'w10NS'(for nanoseconds); note that it is also possible to write 'w10e-9'." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude in Volts." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency in Hz. Values may be 50000 or 50KHZ" )
        
        return parser

    def do_something(self,args):
        if args.channels:
            for chan in args.channels.split(','):
                if args.amplitude:
                    getattr(getattr(self.Instance,f'channel{chan}'),'amplitude')(args.amplitude)
                if args.offset:
                    getattr(getattr(self.Instance,f'channel{chan}'),'offset')(args.offset)
                if args.frequency:
                    getattr(getattr(self.Instance,f'channel{chan}'),'frequency')(args.frequency)
                if args.dc_mode:
                    import time
                    getattr(getattr(self.Instance,f'channel{chan}'),'set_mode')('DC')
                    time.sleep(0.03)     # so ugly.., makes a difference at display
                    getattr(getattr(self.Instance,f'channel{chan}'),'offset')(args.dc_mode)
                if args.pulsemode:
                    if args.pulsemode[0]=="d": 
                        getattr(getattr(self.Instance,f'channel{chan}'),'set_mode')('PULS')
                        getattr(getattr(self.Instance,f'channel{chan}'),'set_pulse_duty_cycle')(args.pulsemode[1:])
                    elif args.pulsemode[0]=="w":
                        getattr(getattr(self.Instance,f'channel{chan}'),'set_mode')('PULS')
                        getattr(getattr(self.Instance,f'channel{chan}'),'set_pulse_width')(args.pulsemode[1:])
                    else: print("pulse mode argument must start with either 'd' or 'w'")
                    

    def exit(self):
        self.Instance.close()
