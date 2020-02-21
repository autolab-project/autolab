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
            
    autolab driver -D {self.name} -A GPIB::7::INSTR -C VISA -a 30 -t 20.1
    load {self.name} driver using VISA communication protocol with address TCPIP... and set the current to 30mA and the temperature to 20.1 degree celcius.
    
    autolab driver -D nickname -p 30 -t 20.1
    same as before but using the device nickname as defined in local_config.ini and set the power setpoint to 30mW
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-a", "--current", type=str, dest="current", default=None, help="Set the current in mA." )
        parser.add_argument("-p", "--power", type=str, dest="power", default=None, help="Set the pump power setpoint in mW." )
        parser.add_argument("-t", "--temperature", type=str, dest="temperature", default=None, help="Set locking temperature." )
        
        return parser

    def do_something(self,args):
        if args.current:
            getattr(getattr(self.Instance,'las'),'set_current')(args.current)
        elif args.power:
            getattr(getattr(self.Instance,'las'),'set_power')(args.power)
        if args.temperature:
            getattr(getattr(self.Instance,'tec'),'set_temperature')(args.temperature)
            

    def exit(self):
        self.Instance.close()
