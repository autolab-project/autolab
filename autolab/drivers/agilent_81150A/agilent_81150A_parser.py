#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import agilent_81150A as MODULE
from argparse import ArgumentParser


class Driver_parser():
    def __init__(self,args,utilities,**kwargs):
        self.name      = args.driver
        self.utilities = utilities
        """Set the connection up"""
        self.classes_list = self.utilities.list_classes(MODULE)
        Driver_class      = self.utilities.identify_device_class(MODULE,self.classes_list,args.link)
        self.Instance     = Driver_class(address=args.address,**kwargs)
        
        self.methods_list = self.utilities.list_methods(self.Instance)
        
        
    def add_parser_arguments(self,parser):
        """Add arguments and help to the parser passed as input"""
        usage = f"""
----------------  Driver informations:  ----------------
{self.help()}

----------------  Examples:  ----------------

usage:    autolab-drivers [options] arg 
        
    autolab-drivers -d {self.name} -i TCPIP::192.168.0.3::INSTR -l VISA -a 1 -o 1 -f 50KHZ -c 1 2
    set the frequency to 50 kHz, the amplitude to 1V, the offset to 1V for both channel 1 and 2

    autolab-drivers -d nickname -p w10NS 1
    set pulse mode to channel 1 with pulse width of 10NS (MS stands for microseconds), using the device nickname as defined in devices_index.ini

    autolab-drivers -d nickname -p d10 2
    set pulse mode to channel 2 with duty cycle of 10 purcent, using the device nickname as defined in devices_index.ini
    
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-c", "--channels", nargs='+', type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-o", "--offset", type=str, dest="offset", default=None, help="Set the offset value." )
        parser.add_argument("-u", "--uniform", type=str, dest="uniform", default=None, help="Set dc mode on and set offset." )
        parser.add_argument("-p", "--pulsemode", type=str, dest="pulsemode", default=None, help="Set pulse mode and use argument as either the duty cycle or the pulse width depending on the first letter 'd' or 'w' (see examples)." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency. Values may be 50000 or 50KHZ" )
        
        return parser

    def help(self):
        """Add to the help lists of module: classes, methods and arguments"""
        classes_list = self.utilities.print_help_classes(self.classes_list)                  # display list of classes in module
        methods_list = self.utilities.print_help_methods(self.methods_list)                  # display list of methods in module
        methods_args = self.utilities.print_help_methods_arguments(self.Instance,self.methods_list)      # display list of methods arguments
        return classes_list + methods_list + methods_args

    def do_something(self,args):
        if args.channels:
            for chan in args.channels:
                if args.amplitude:
                    getattr(getattr(self.Instance,f'channel{chan}'),'amplitude')(args.amplitude)
                if args.offset:
                    getattr(getattr(self.Instance,f'channel{chan}'),'offset')(args.offset)
                if args.frequency:
                    getattr(getattr(self.Instance,f'channel{chan}'),'frequency')(args.frequency)
                if args.uniform:
                    getattr(getattr(self.Instance,f'channel{chan}'),'dc_mode')(args.uniform)
                if args.pulsemode:
                    if args.pulsemode[0]=="d": 
                        getattr(getattr(self.Instance,f'channel{chan}'),'pulse_mode')(duty_cycle=args.pulsemode[1:])
                    elif args.pulsemode[0]=="w":
                        getattr(getattr(self.Instance,f'channel{chan}'),'pulse_mode')(width=args.pulsemode[1:])
                    else: print("pulse mode argument must start with either 'd' or 'w'")
        
        if args.methods:
            methods = [args.methods[i].split(',') for i in range(len(args.methods))]
            message = self.utilities.parse_commands(self.Instance,methods,self.methods_list)

    def exit(self):
        self.Instance.close()
        sys.exit()
