#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import agilent_33220A as MODULE
from argparse import ArgumentParser


class driver_parser():
    def __init__(self,args,utilities,**kwargs):
        """Set the connection up"""
        self.classes_list = utilities.list_classes(MODULE)
        Driver_class      = utilities.identify_device_class(MODULE,self.classes_list,args.link)
        self.Instance     = Driver_class(address=args.address,**kwargs)
        
        self.methods_list = utilities.list_methods(self.Instance)
        
        
    def add_parser_arguments(self,parser):
        """Add arguments and help to the parser passed as input"""
        usage = """usage: %prog [options] arg
                    
                    
                    EXAMPLES:
                        
                    

                    """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-r", "--ramp", type=float, dest="ramp", default=None, help="Turn on ramp mode." )
        parser.add_argument("-o", "--offset", type=str, dest="offset", default=None, help="Set the offset value." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency." )
        
        return parser

    def help(self):
        """Add to the help lists of module: classes, methods and arguments"""
        utilities.print_help_classes(self.classes_list)                  # display list of classes in module
        utilities.print_help_methods(self.methods_list)                  # display list of methods in module
        utilities.print_help_methods_arguments(self.Instance,self.methods_list)      # display list of methods arguments

    def do_something(self,args):
        if args.amplitude:
            self.Instance.amplitude(args.amplitude)
        if args.offset:
            self.Instance.offset(args.offset)
        if args.frequency:
            self.Instance.frequency(args.frequency)
        if args.ramp:
            self.Instance.ramp(args.ramp)
        if args.command:
            commands = [args.command[i].split(',') for i in range(len(args.command))]
            message = utilities.parse_commands(self.Instance,commands,self.methods_list)

    def exit(self):
        #I.close()
        sys.exit()
