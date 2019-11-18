#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Optical frame'

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
            
    autolab driver -D {self.name} -C VISA -A GPIB0::2::INSTR -c 3,5 -p 30
    load {self.name} driver using VISA and local network address 192.168.0.4 and set the power to 30 mW to slots 3 and 5
    
    autolab driver -D nickname -c 3 -w 1550.1
    Similar to previous one but using the device's nickname as defined in the local_config.ini, and set the wavelength to 1550.1

    Note: Arbitrary waveform available only using a python terminal
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-c", "--channels",type=str, dest="channels", default=None, help="Set the slots to act on/acquire from." )
        parser.add_argument("-p", "--power",type=str, dest="power", default=None, help="Set the power in mW." )
        parser.add_argument("-w", "--wavelength",type=str, dest="wavelength", default=None, help="Set the wavelength in nm." )
        
        return parser

    def do_something(self,args):
        if args.channels:
            for chan in args.channels.split(','):
                assert f'{chan}' in getattr(self.Instance,f'slot_names').keys()
                name_sub_module = getattr(self.Instance,f'slot_names')[f'{chan}']
                sub_module = getattr(self.Instance,name_sub_module)
                if args.power:
                    func_name = 'set_power'
                    assert hasattr(sub_module,func_name), "Module has no attribute {func_name}, are you addressing the right slot?"
                    getattr(sub_module,func_name)(args.power)
                if args.wavelength:
                    func_name = 'set_wavelength'
                    assert hasattr(sub_module,func_name), "Module has no attribute {func_name}, are you addressing the right slot?"
                    getattr(sub_module,func_name)(args.wavelength)


    def exit(self):
        self.Instance.close()

