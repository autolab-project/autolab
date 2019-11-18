#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Optical amplifier'
    
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
            
    autolab driver -D {self.name} -A GPIB::2::INSTR -C VISA -p 100
    load {self.name} driver using VISA communication protocol with address GPIB... and set the power to 10dBm
    
    autolab driver -D nickname -p 1
    same as before but using the device nickname as defined in local_config.ini
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-p", "--power", type=str, dest="power", default=None, help="Set the pump power setpoint in 1/10dBm (e.g. 100 <=> 10dBm; this conversion may depend on the model, please verify)." )
        
        return parser

    def do_something(self,args):
        if args.power:
            getattr(self.Instance,'set_power')(args.power)
            
            
    def exit(self):
        self.Instance.close()
