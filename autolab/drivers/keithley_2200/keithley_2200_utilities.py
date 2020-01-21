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
            
    autolab driver -D {self.name} -A GPIB::7::INSTR -C VISA -v 0.2
    load {self.name} driver using VISA communication protocol with address GPIB... and set the voltage to 0.2V 
    
    autolab driver -D nickname -a 0.5
    using the device nickname as defined in local_config.ini modify the current compliance to 0.5 A
    
    autolab driver -D nickname -s 0
    using the device nickname as defined in local_config.ini, turn the output OFF
    
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-v", "--voltage", type=str, dest="voltage", default=None, help="Set the voltage in V." )
        parser.add_argument("-a", "--current", type=str, dest="current", default=None, help="Set the current in A." )
        parser.add_argument("-s", "--state", type=str, dest="state", default=None, help="Turn output OFF or ON: arguments are 0 or 1 (for OFF and ON, respectively)." )
        
        return parser

    def do_something(self,args):
        if args.voltage:
            getattr(self.Instance,'set_voltage_compliance')(args.voltage)
        if args.current:
            getattr(self.Instance,'set_current_compliance')(args.current)
        if args.state:
            assert isinstance(bool(int(float(args.state))),bool)
            args.state = bool(int(float(args.state)))
            getattr(self.Instance,'set_output_state')(args.state)
            
    def exit(self):
        self.Instance.close()
