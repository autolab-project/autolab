#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import agilent_33220A as MODULE
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
            
    autolab-drivers -d {self.name} -i TCPIP::192.168.0.4::INSTR -l VISA -a 0.5 -f 500
    load {self.name} driver with address TCPIP... and using VISA communication protocol and set the amplitude to 0.5V and frequency to 500Hz.
    
    autolab-drivers -d nickname -a 0.5 -f 500
    same as before but using the device nickname as defined in devices_index.ini

            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-r", "--ramp", type=float, dest="ramp", default=None, help="Turn on ramp mode." )
        parser.add_argument("-o", "--offset", type=str, dest="offset", default=None, help="Set the offset value." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency." )
        
        return parser

    def help(self):
        """Add to the help lists of module: classes, methods and arguments"""
        classes_list = self.utilities.print_help_classes(self.classes_list)                  # display list of classes in module
        methods_list = self.utilities.print_help_methods(self.methods_list)                  # display list of methods in module
        methods_args = self.utilities.print_help_methods_arguments(self.Instance,self.methods_list)      # display list of methods arguments
        return classes_list + methods_list + methods_args

    def do_something(self,args):
        if args.amplitude:
            self.Instance.amplitude(args.amplitude)
        if args.offset:
            self.Instance.offset(args.offset)
        if args.frequency:
            self.Instance.frequency(args.frequency)
        if args.ramp:
            self.Instance.ramp(args.ramp)
        if args.methods:
            methods = [args.methods[i].split(',') for i in range(len(args.methods))]
            message = self.utilities.parse_commands(self.Instance,methods,self.methods_list)

    def exit(self):
        #I.close()
        sys.exit()
