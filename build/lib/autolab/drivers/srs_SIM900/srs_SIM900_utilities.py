#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Electrical frame'

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
            
    autolab driver -D {self.name} -C VISA -A GPIB0::2::INSTR -c 3,5 -s 2
    load {self.name} driver using VISA and local network address 192.168.0.4 and set setpoint of SIM960(PID controller) to 2V module inserted in slots 3 and 5
    
    autolab driver -D nickname -c 2 -r 
    Similar to previous one but using the device's nickname as defined in local_config.ini and set output to pid control.
    
    autolab driver -D nickname -c 2 -u
    Similar to previous one but using the device's nickname as defined in local_config.ini and set output to manual.
    
    autolab driver -D nickname -c 2 -a
    Similar to previous one but using the device's nickname as defined in local_config.ini and set output to manual to unlock and try relock.
    
    Note: Arbitrary waveform available only using a python terminal
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
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


    def exit(self):
        self.Instance.close()

