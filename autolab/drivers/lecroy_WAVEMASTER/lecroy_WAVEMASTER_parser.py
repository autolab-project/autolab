#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import agilent_MXAN9020A as MODULE
from argparse import ArgumentParser


class Driver_parser():
    def __init__(self,args,utilities,**kwargs):
        self.utilities = utilities
        """Set the connection up"""
        self.classes_list = self.utilities.list_classes(MODULE)
        Driver_class      = self.utilities.identify_device_class(MODULE,self.classes_list,args.link)
        self.Instance     = Driver_class(address=args.address,**kwargs)
        
        self.methods_list = self.utilities.list_methods(self.Instance)
        
        
    def add_parser_arguments(self,parser):
        """Add arguments and help to the parser passed as input"""
        usage = f"""
----------------  Driver informations:  ----------------
{self.help()}

----------------  Extra infos:  ----------------
    - Datas are obtained in a binary format: int8 
    - To retrieve datas (in "VERTUNIT"), see corresponding log file:
    DATA(VERTUNIT) = DATA(ACQUIRED) * VERTICAL_GAIN - VERTICAL_OFFSET

----------------  Examples:  ----------------

usage:    autolab-drivers [options] arg 
        
    autolab-drivers -d {MODULE.__name__} -i 192.168.0.3 -l VXI11 -o my_output_file -c 1 2
    Results in saving two files for the trace 1, the data and the scope parameters, called respectively my_output_file_DSACHAN1 and my_output_file_DSACHAN1.log
    
    autolab-drivers -d nickname -o my_output_file -e WORD 
    Same as previous will save all channels as None are specified and using the device nickname as defined in devices_index.ini. the encoding is set to WORD
    
    
    
    autolab-drivers -d nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-c", "--channels", nargs='+', type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-o", "--filename", type=str, dest="filename", default='DEFAULT', help="Set the name of the output file" )
        parser.add_argument("-F", "--force",action="store_true", dest="force", default=None, help="Allows overwriting file" )
        parser.add_argument("-t", "--trigger", type=str, dest="trigger",action="store_true", help="Trigger the scope once" )
        parser.add_argument("-f", "--format", type=str, dest="format", default='BYTE', help="Change data encoding" )
        
        
        
   #parser.add_option("-m", "--spe_mode", type="string", dest="spe_mode", default=None, help="For allowing auto modification of the vertical gain. List of: spe_mode iteration number, all the channels to apply spe mode to. Note if no channel specified, all the channel are corrected. WARNING: if you want all the channels to correpond to the same trigger event, you need to spe_mode one channel only and to physically plug the cable in the first channel acquired (first in the list 1->4)")
   #parser.add_option("-n", "--spe_fact", type="float", dest="spe_fact", default=8., help="For setting limits of the vertical gain, units are in number of scope divisions here. WARNING: Do not overpass 9 due to a security in the code! WARNING: the number of vertical divisions might depend on the scope (8 or 10 usually)." )
   #parser.add_option("-t", "--trigger", action="store_true", dest="trigger", default=False, help="Ask the scope to trigger once before acquiring." )

        
        return parser

    def do_something(self,args):
        if args.format:
            getattr(self.Instance,'set_encoding')(args.format)
        if args.filename:
            getattr(self.Instance,'get_data_channels')(channels=args.channels,single=args.trigger)
            getattr(self.Instance,'save_data_channels')(filename=args.filename,channels=args.channels,FORCE=args.FORCE)
  
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
