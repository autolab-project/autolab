#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tektronix_TDS5104B as MODULE
from argparse import ArgumentParser


class Driver_parser():
    def __init__(self,args,utilities,**kwargs):
        self.utilities = utilities
        """Set the connection up"""
        self.classes_list = self.utilities.list_classes(MODULE)
        Driver_class      = self.utilities.identify_device_class(MODULE,self.classes_list,args.link)
        
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
    Datas are recorded in int8 format
    
    Headers contains:
    :WFMOUTPRE:BYT_NR 2;BIT_NR 16;ENCDG ASCII;BN_FMT RI;BYT_OR
    MSB;WFID 'Ch1, DC coupling, 100.0mV/div, 4.000us/div, 10000
    points, Sample mode';NR_PT 10000;PT_FMT Y;XUNIT 's';XINCR
    4.0000E-9;XZERO - 20.0000E-6;PT_OFF 0;YUNIT 'V';YMULT
    15.6250E-6;YOFF :”6.4000E+3;YZERO 0.0000
    
    To retrieve real value:
    value_in_units = ((curve_in_dl - YOFf_in_dl) * YMUlt) + YZEro_in_units

----------------  Examples:  ----------------

usage:    autolab-drivers [options] arg 
        
    autolab-drivers -d {MODULE.__name__} -i 192.168.0.3 -l VXI11 -o my_output_file -c 1
    Results in saving two files for the temporal trace of channel 1, the data and the scope parameters, called respectively my_output_file_TDS5104BCH1 and my_output_file_TDS5104BCH1.log
    
    autolab-drivers -d nickname -o my_output_file -F -c 1,2
    Same as previous one but with 4 output files, two for each channel (1 and 2) and using the device nickname as defined in devices_index.ini. If files with your filename already exist -F flag overwrite them.
    
    autolab-drivers -d nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-o", "--filename", type=str, dest="filename", default=None, help="Set the name of the output file" )
        parser.add_argument("-F", "--force",action="store_true", dest="force", default=None, help="Allows overwriting file" )
        
        return parser

    def do_something(self,args):
        if args.filename:
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
