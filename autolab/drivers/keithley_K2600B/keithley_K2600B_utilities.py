#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Electrical source'
    
    
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
            
    autolab driver -D {self.name} -A GPIB::7::INSTR -C VISA -v 0.2 -c A,B
    load {self.name} driver using VISA communication protocol with address TCPIP... and set the voltage to 0.2V to channel A and B
    
    autolab driver -D nickname -v 0.2 -c A
    same as before but using the device nickname as defined in local_config.ini
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the channels to act on." )
        parser.add_argument("-v", "--voltage", type=str, dest="voltage", default=None, help="Set the voltage in V." )
        parser.add_argument("-a", "--current", type=str, dest="current", default=None, help="Set the current in A." )
        
        return parser

    def do_something(self,args):
        if args.channels:
            for chan in args.channels.split(','):
                if args.voltage:
                    getattr(getattr(self.Instance,f'channel{chan}'),'set_voltage')(args.voltage)
                if args.current:
                    getattr(getattr(self.Instance,f'channel{chan}'),'set_current')(args.current)
            

    def exit(self):
        self.Instance.close()
