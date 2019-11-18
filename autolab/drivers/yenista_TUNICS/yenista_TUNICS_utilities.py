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
            
    autolab driver -D {self.name} -C VISA -A GPIB0::2::INSTR -w 1550.2 -p 10
    load {self.name} driver using VISA communication protocol with address GPIB... and set the wavelength to 1550.2nm and the power to 10mW.
    
    autolab driver -D nickname -a 100
    Use now the device nickname as defined in local_config.ini and set the pump current to 100mA.

    Note: you should provide either current or power at a time (same thing applies to frequency and wavelength)
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-a", "--current", type=str, dest="current", default=None, help="Set the pump current in mA." )
        parser.add_argument("-p", "--power", type=str, dest="power", default=None, help="Set the output power in mW." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the operating frequency in GHz." )
        parser.add_argument("-w", "--wavelength", type=str, dest="wavelength", default=None, help="Set the operating wavelength in nm." )
        return parser

    def do_something(self,args):
        if args.wavelength: 
            assert args.wavelength or args.frequency, "Please provide EITHER wavelength OR frequency"
            getattr(self.Instance,'set_wavelength')(args.wavelength)
        elif args.frequency: 
            getattr(self.Instance,'set_frequency')(args.frequency)
        if args.current: 
            assert args.current or args.power, "Please provide EITHER current OR power"
            getattr(self.Instance,'set_intensity')(args.current)
        elif args.power: getattr(self.Instance,'set_power')(args.power)
        

    def exit(self):
        self.Instance.close()

