#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import srs_SIM900 as MODULE
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
            
    autolab-drivers -D {MODULE.__name__} -C VISA -A GPIB0::2::INSTR -c 3,5 -s 2
    load {MODULE.__name__} driver using VISA and local network address 192.168.0.4 and set setpoint of SIM960(PID controller) to 2V module inserted in slots 3 and 5
    
    autolab-drivers -D nickname -c 2 -r 
    Similar to previous one but using the device's nickname as defined in local_config.ini and set output to pid control.
    
    autolab-drivers -D nickname -c 2 -u
    Similar to previous one but using the device's nickname as defined in local_config.ini and set output to manual.
    
    autolab-drivers -D nickname -c 2 -a
    Similar to previous one but using the device's nickname as defined in local_config.ini and set output to manual to unlock and try relock.
    
    autolab-drivers -D nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
    
    Note: Arbitrary waveform available only using a python terminal
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-c", "--channels",type=str, dest="channels", default=None, help="Set the slots to act on/acquire from." )
        parser.add_argument("-s", "--setpoint",type=str, dest="setpoint", default=None, help="Setpoint value to be used in Volts (for SIM960 PID controller)" )
        parser.add_argument("-r", "--relock",action="store_true", dest="lock", default=False, help="Lock (for SIM960 PID controller)" )
        parser.add_argument("-u", "--unlock",action="store_true", dest="unlock", default=False, help="Unlock (for SIM960 PID controller)" )
        parser.add_argument("-a", "--auto_lock",action="store_true", dest="auto_lock", default=False, help="Choose automatically to unlock and relock in order to decrease the output voltage (for SIM960 PID controller)" )
        
        return parser

    def do_something(self,args):
        if args.channels:
            for chan in args.channels.split(','):
                assert f'{chan}' in getattr(self.Instance,f'slot_names').keys()
                name_sub_module = getattr(self.Instance,f'slot_names')[f'{chan}']
                sub_module = getattr(self.Instance,name_sub_module)
                if args.setpoint:
                    func_name = 'set_setpoint'
                    assert hasattr(sub_module,func_name), "Module has no attribute {func_name}, are you addressing the right slot?"
                    getattr(sub_module,func_name)(args.setpoint)
                if args.relock:
                    func_name = 'relock'
                    assert hasattr(sub_module,func_name), "Module has no attribute {func_name}, are you addressing the right slot?"
                    getattr(sub_module,func_name)()
                elif args.unlock:
                    func_name = 'set_output_manual'
                    assert hasattr(sub_module,func_name), "Module has no attribute {func_name}, are you addressing the right slot?"
                    getattr(sub_module,func_name)()
                elif args.auto_lock:
                    func_name = 'auto_lock'
                    assert hasattr(sub_module,func_name), "Module has no attribute {func_name}, are you addressing the right slot?"
                    getattr(sub_module,func_name)()

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
