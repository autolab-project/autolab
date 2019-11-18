#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Function generator'

class Driver_parser():
    def __init__(self, Instance, name, **kwargs):
        self.name     = name
        self.Instance = Instance
        
        
    def add_parser_usage(self,message):
        """Add arguments and help to the parser passed as input"""
        s = f"""
----------------  Driver informations:  ----------------
    {message}

----------------  Examples:  ----------------

usage:    autolab-drivers [options] arg
            
    autolab-drivers -D {MODULE.__name__} -A TCPIP::192.168.0.4::INSTR -C VISA -a 0.5 -f 500
    load {MODULE.__name__} driver using VISA communication protocol with address TCPIP... and set the amplitude to 0.5V and frequency to 500Hz.
    
    autolab-drivers -D nickname -a 0.5 -f 500
    same as before but using the device nickname as defined in local_config.ini
            """
        return s
    
    def add_parser_arguments(self,parser):
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-r", "--ramp", type=float, dest="ramp", default=None, help="Turn on ramp mode." )
        parser.add_argument("-o", "--offset", type=str, dest="offset", default=None, help="Set the offset value in Volts." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude in Volts." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency in Hz." )
        
        return parser

    def do_something(self,args):
        if args.amplitude:
            getattr(self.Instance,'amplitude')(args.amplitude)
        if args.offset:
            getattr(self.Instance,'offset')(args.offset)
        if args.frequency:
            getattr(self.Instance,'frequency')(args.frequency)
        if args.ramp:
            getattr(self.Instance,'ramp')(args.ramp)
        if args.methods:
            methods = [args.methods[i].split(',') for i in range(len(args.methods))]
            message = self.utilities.parse_commands(self.Instance,methods,self.methods_list)

    def help(self,parser):
        """Add to the help lists of module: classes, methods and arguments"""
        classes_list = self.utilities.print_help_classes(self.classes_list)                  # display list of classes in module
        methods_list = self.utilities.print_help_methods(self.methods_list)                  # display list of methods in module
        methods_args = self.utilities.print_help_methods_arguments(self.Instance,self.methods_list)      # display list of methods arguments
        return parser, classes_list + methods_list + methods_args

    def exit(self):
        self.Instance.close()
