#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import yenista_TUNICS as MODULE
from argparse import ArgumentParser

category = 'Optical source'

class Driver_parser():
    def __init__(self,args,utilities,**kwargs):
        self.utilities = utilities
        """Set the connection up"""
        self.classes_list = self.utilities.list_classes(MODULE)
        Driver_class      = self.utilities.identify_device_class(MODULE,self.classes_list,args.connection)
        
        # pass the argument board_index or libpath argument through port one
        kwargs = self.utilities.parsekwargs_connectiondependant(kwargs=kwargs,Driver_class=Driver_class)
        self.Instance     = Driver_class(address=args.address,**kwargs)
        
        self.methods_list = self.utilities.list_methods(self.Instance)
        
        
    def add_parser_arguments(self,parser):
        """Add arguments and help to the parser passed as input"""
        usage = f"""
----------------  Driver informations:  ----------------
{self.help()}

----------------  Examples:  ----------------

usage:    autolab-drivers [options] arg 
            
    autolab-drivers -D {MODULE.__name__} -C VISA -A GPIB0::2::INSTR -w 1550.2 -p 10
    load {MODULE.__name__} driver using VISA communication protocol with address GPIB... and set the wavelength to 1550.2nm and the power to 10mW.
    
    autolab-drivers -D nickname -a 100
    Use now the device nickname as defined in local_config.ini and set the pump current to 100mA.
    
    autolab-drivers -D nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
    
    Note: you should provide either current or power at a time (same thing applies to frequency and wavelength)
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
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
        
        if args.methods:
            methods = [args.methods[i].split(',') for i in range(len(args.methods))]
            message = self.utilities.parse_commands(self.Instance,methods,self.methods_list)

    def help(self):
        """Add to the help lists of module: classes, methods and arguments"""
        classes_list = self.utilities.print_help_classes(self.classes_list)                  # display list of classes in module
        methods_list = self.utilities.print_help_methods(self.methods_list)                  # display list of methods in module
        methods_args = self.utilities.print_help_methods_arguments(self.Instance,self.methods_list)      # display list of methods arguments
        return classes_list + methods_list + methods_args

    def exit(self):
        self.Instance.close()

