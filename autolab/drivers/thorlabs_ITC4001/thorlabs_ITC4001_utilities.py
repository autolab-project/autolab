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
            
    autolab driver -D {self.name} -A GPIB0::2::INSTR -C VISA -a 0.2
    load {self.name} driver using VISA communication protocol with address GPIB... and set the laser pump current to 200mA.
    
    autolab driver -D nickname -a 0.2
    Similar to previous one but using the device's nickname as defined in local_config.ini
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the pump current value in Ampere." )
        
        return parser

    def do_something(self,args):
        if args.amplitude:
            getattr(self.Instance,'amplitude')(args.amplitude)


    def exit(self):
        self.Instance.close()
