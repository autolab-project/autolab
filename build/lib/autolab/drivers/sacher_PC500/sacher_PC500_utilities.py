#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Optical source'

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

    autolab driver -D {self.name} -A TCPIP::192.168.0.4::INSTR -C VISA -a 0.5
    load {self.name} driver using VISA communication protocol with address TCPIP... and set the amplitude to 0.5V
    
    autolab driver -D nickname -a 0.5
    same as before but using the device nickname as defined in local_config.ini
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-c", "--current", type=float, dest="current", default=None, help="Set the laser current in mA." )
        return parser

    def do_something(self,args):
        if args.current:
            getattr(self.Instance,'current')(args.current)

    def exit(self):
        self.Instance.close()
