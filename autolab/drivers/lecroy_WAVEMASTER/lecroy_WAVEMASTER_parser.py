#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import lecroy_WAVEMASTER as MODULE
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
    - Datas are obtained in a binary format: int8 
    - To retrieve datas (in "VERTUNIT"), see corresponding log file:
    DATA(VERTUNIT) = DATA(ACQUIRED) * VERTICAL_GAIN - VERTICAL_OFFSET

----------------  Examples:  ----------------

usage:    autolab-drivers [options] arg 
        
    autolab-drivers -d {MODULE.__name__} -i 192.168.0.3 -l VXI11 -o my_output_file -c 1,2
    Results in saving two files for the trace 1, the data and the scope parameters, called respectively my_output_file_DSACHAN1 and my_output_file_DSACHAN1.log
    
    autolab-drivers -d nickname -o my_output_file -e WORD 
    Same as previous will save all channels as None are specified and using the device nickname as defined in devices_index.ini. the encoding is set to WORD
    
    autolab-drivers -d nickname -o my_output_file -a 5,1,3 -b 8
    Vertical autoscale will be enabled for channels 1 and 3. They will both go through the optimization loop 5 times, and aiming 8 vertical divisions.
    
    autolab-drivers -d nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-o", "--filename", type=str, dest="filename", default=None, help="Set the name of the output file" )
        parser.add_argument("-F", "--force",action="store_true", dest="force", default=None, help="Allows overwriting file" )
        parser.add_argument("-t", "--trigger", type=str, dest="trigger",action="store_true", help="Trigger the scope once" )
        parser.add_argument("-f", "--format", type=str, dest="format", default=None, help="Change data encoding" )
        parser.add_option("-a", "--auto_scale", type="string", dest="auto_scale", default=None, help="To allow auto modification of the vertical gain. Argument is a list of: auto_scale iteration number, all the channels to apply spe mode to. Note if no channel specified, all the channels are corrected. WARNING: Specifying more than one channel to apply auto_scale to will result in different trigger events for the acquiered channels.")
        parser.add_option("-b", "--auto_fact", type="float", dest="auto_fact", default=None, help="For setting limits of the vertical gain, units are in number of scope divisions here. WARNING: Do not overpass 9 due to a security in the code! WARNING: the number of vertical divisions might depend on the scope (8 or 10 usually)." )

        return parser

    def do_something(self,args):
        if args.format:
            getattr(self.Instance,'set_encoding')(args.format)
        if args.trigger and not args.filename:
            getattr(self.Instance,'single')()
        if args.auto_scale: # test must be located before args.filename's one
            for chan in arg.auto_scale.split(',')[1:]:
                getattr(getattr(self.Instance,f'channel{chan}'),'set_autoscale_iter')(args.auto_scale.split(',')[0])
        if args.auto_fact: # test must be located before args.filename's one
            for chan in range(1,getattr(self.Instance,'nb_channels')+1):
                getattr(getattr(self.Instance,f'channel{chan}'),'set_autoscale_factor')(args.auto_fact) # all channels instances
        if args.filename:
            getattr(self.Instance,'get_data_channels')(channels=args.channels.split(','),single=args.trigger)
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
