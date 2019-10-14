#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aimtti_TGF3162 as MODULE
from argparse import ArgumentParser


class Driver_parser():
    def __init__(self,args,utilities,**kwargs):
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
            
    autolab-drivers -d {MODULE.__name__} -l SOCKET -a 0.5 -f 80000000 -c 1 2
    load {MODULE.__name__} driver using socket and set the channel 1 and 2 amplitude to 0.5V and frequency to 80MHz.
    
    autolab-drivers -d nickname -a 0.5 -f 80e6 -c 1
    same as before but using the device nickname as defined in devices_index.ini and only for channel 1.
    
    autolab-drivers -d nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
    
    Note: Arbitrary waveform available only using a python terminal
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-c", "--channels", nargs='+', type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency." )
        parser.add_argument("-p", "--period", type=str, dest="period", default=None, help="Set the period." )
        
        return parser

    def do_something(self,args):
        if args.channels:
            for chan in args.channels:
                if args.amplitude:
                    getattr(getattr(self.Instance,f'channel{chan}'),'amplitude')(args.amplitude)
                if args.frequency:
                    getattr(getattr(self.Instance,f'channel{chan}'),'frequency')(args.frequency)
                if args.offset:
                    getattr(getattr(self.Instance,f'channel{chan}'),'offset')(args.offset)

        if args.methods:
            methods = [args.methods[i].split(',') for i in range(len(args.methods))]
            message = self.utilities.parse_commands(self.Instance,methods,self.methods_list)

    def help(self):
        """Add to the help lists of module: classes, methods and arguments"""
        classes_list = self.utilities.print_help_classes(self.classes_list)                  # display list of classes in module
        methods_list = self.utilities.print_help_methods(self.methods_list)                  # display list of methods in module
        methods_args = self.utilities.print_help_methods_arguments(self.Instance,self.methods_list)      # display list of methods arguments
        return classes_list + methods_list + methods_args

    def exit(self):
        self.Instance.close()
        sys.exit()
