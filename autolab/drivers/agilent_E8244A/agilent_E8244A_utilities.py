#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Function generator'

class Driver_parser():
    def __init__(self, Instance, name, **kwargs):
        self.name     = name
        self.Instance = Instance
        
        
    def add_parser_usage(self,message):
        """Usage to be used by the parser"""
        usage = f"""
{message}

----------------  Examples:  ----------------

usage:    autolab driver [options] args
            
    autolab driver -D {self.name} -A TCPIP::192.168.0.4::INSTR -C VISA -a 0.5 -f 500
    load {self.name} driver using VISA communication protocol with address TCPIP... and set the amplitude to 0.5V and frequency to 500Hz.
    
    autolab driver -D nickname -a 0.5 -f 500
    same as before but using the device nickname as defined in local_config.ini
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency." )
        
        return parser

    def do_something(self,args):
        if args.amplitude:
            getattr(self.Instance,'amplitude')(args.amplitude)
        if args.frequency:
            getattr(self.Instance,'frequency')(args.frequency)


    def exit(self):
        self.Instance.close()
