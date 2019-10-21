#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import agilent_DSO81204B as MODULE
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

----------------  Extra infos:  ----------------
    - Datas are obtained in a binary format: int8 
    - Header is composed as follow:
    <format>, <type>, <points>, <count> , <X increment>, <X origin>, < X reference>, <Y increment>, <Y origin>, <Y reference>, <coupling>, <X display range>, <X display origin>, <Y display range>, <Y display origin>, <date>,
    <time>, <frame model #>, <acquisition mode>, <completion>, <X units>, <Y units>, <max bandwidth limit>, <min bandwidth limit>    
    - To retrieve datas (in "Units")
    Y-axis Units = data value * Yincrement + Yorigin (analog channels) 
    X-axis Units = data index * Xincrement + Xorigin

----------------  Examples:  ----------------

usage:    autolab-drivers [options] arg 
        
    autolab-drivers -D {MODULE.__name__} -A 192.168.0.3 -C VXI11 -o my_output_file -c 1
    Results in saving two files for the temporal trace of channel 1, the data and the scope parameters, called respectively my_output_file_DSACHAN1 and my_output_file_DSACHAN1.log
    
    autolab-drivers -D nickname -o my_output_file -c 1,2
    Same as previous one but with 4 output files, two for each channel (1 and 2) and using the device nickname as defined in local_config.ini
    
    autolab-drivers -D nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-o", "--filename", type=str, dest="filename", default=None, help="Set the name of the output file" )
        parser.add_argument("-m", "--measure", type=str, dest="measure", default=None, help="Set measurment number" )
        parser.add_argument("-F", "--force",action="store_true", dest="force", default=None, help="Allows overwriting file" )
        parser.add_argument("-t", "--trigger", type=str, dest="trigger",action="store_true", help="Trigger the scope once" )
        parser.add_argument("-f", "--format", type=str, dest="format", default=None, help="Change data encoding" )
        
        return parser

    def do_something(self,args):
        if args.format:
            getattr(self.Instance,'set_type')(args.format)
        if args.trigger:
            getattr(self.Instance,'single')()
        if args.measure:
            for i in range(args.measure):
                getattr(self.Instance,'stop')()
                print(str(i+1))
                getattr(self.Instance,'get_data_channels')(channels=args.channels.split(','))
                getattr(self.Instance,'save_data_channels')(filename=str(i+1),channels=args.channels.split(','),FORCE=args.force)
                getattr(self.Instance,'run')()
                time.sleep(0.050)
        elif args.filename:
            getattr(self.Instance,'get_data_channels')(channels=args.channels.split(','))
            getattr(self.Instance,'save_data_channels')(filename=args.filename,channels=args.channels.split(','),FORCE=args.force)
  
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
