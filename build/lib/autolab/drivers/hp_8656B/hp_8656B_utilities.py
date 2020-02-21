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
            
    autolab driver -D {self.name} -A GPIB::7::INSTR -C VISA -a 0.5 -f 10e6
    load {self.name} driver using VISA communication protocol with address TCPIP... and set the amplitude to 0.5V and frequency to 10MHz.
    
    autolab driver -D nickname -a 0.5 -f  10e6
    same as before but using the device nickname as defined in local_config.ini
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-e", "--enable", action='store_true', dest="enable", default=None, help="Turn the RF output on." )
        parser.add_argument("-d", "--disable", action='store_true', dest="disable", default=None, help="Turn the RF output off." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency." )
        
        return parser

    def do_something(self,args):
        if args.amplitude:
            getattr(self.Instance,'set_rfamp')(args.amplitude)
        if args.frequency:
            getattr(self.Instance,'set_frequency')(args.frequency)
        if args.enable:
            getattr(self.Instance,'RFenable')()
        if args.disable:
            getattr(self.Instance,'RFdisable')()


    def exit(self):
        #self.Instance.close()
        pass
