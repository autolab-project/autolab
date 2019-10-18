#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yenista_OSICS as MODULE
from argparse import ArgumentParser


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
            
    autolab-drivers -D {MODULE.__name__} -C VISA -A GPIB0::2::INSTR -c 3,5 -p 30
    load {MODULE.__name__} driver using VISA and local network address 192.168.0.4 and set the power to 30 mW to slots 3 and 5
    
    autolab-drivers -D nickname -c 3 -w 1550.1
    Similar to previous one but using the device's nickname as defined in the devices_index.ini, and set the wavelength to 1550.1
    
    autolab-drivers -D nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
    
    Note: Arbitrary waveform available only using a python terminal
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-c", "--channels",type=str, dest="channels", default=None, help="Set the slots to act on/acquire from." )
        parser.add_argument("-p", "--power",type=str, dest="power", default=None, help="Set the power in mW." )
        parser.add_argument("-w", "--wavelength",type=str, dest="wavelength", default=None, help="Set the wavelength in nm." )
        
        return parser

    def do_something(self,args):
        if args.channels:
            for chan in args.channels.split(','):
                assert f'{chan}' in getattr(self.Instance,f'{slotnames}').keys()
                name_sub_module = getattr(self.Instance,f'{slotnames}')[f'{chan}']
                sub_module = getattr(self.Instance,name_sub_module)
                if args.power:
                    func_name = 'setPower'
                    assert hasattr(sub_module,func_name), "Module has no attribute {func_name}, are you addressing the right slot?"
                    getattr(sub_module,func_name)(args.power)
                if args.wavelength:
                    func_name = 'setWavelength'
                    assert hasattr(sub_module,func_name), "Module has no attribute {func_name}, are you addressing the right slot?"
                    getattr(sub_module,func_name)(args.wavelength)

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
        sys.exit()
