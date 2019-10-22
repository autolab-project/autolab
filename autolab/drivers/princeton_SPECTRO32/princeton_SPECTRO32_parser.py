#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import princeton_SPECTRO32 as MODULE
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
            
    autolab-drivers -D {MODULE.__name__} -C SOCKET -A 192.168.0.2 -c Camera1 -n 2 -e 0.1 -o my_file_name
    load {MODULE.__name__} driver using SOCKET communication protocol with address 192.168.0.2 and acquire data from Camera1 after 2 expositions of 0.1s each. Save those into my_file_name.txt.
    
    autolab-drivers -D nickname -a -c Camera1 -o my_file_name
    Similar to previous one using device's nickname defined in local_config.ini, get and save the data using auto vertical scale/exposure optimization loop (so as to maximize signal vertically).

    autolab-drivers -D nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-c", "--camera", type=str, dest="camera", default=None, help="Set the camera to get the data from." )
        parser.add_argument("-n", "--nb_frames", type=str, dest="nb_frames", default=None, help="Set the number of frames to acquire" )
        parser.add_argument("-e", "--exposure", type=str, dest="exposure", default=None, help="Set the exposure time in s" )
        parser.add_argument("-o", "--filename", type=str, dest="filename", default=None, help="Set the name of the output file" )
        parser.add_argument("-a", "--auto_exposure", action = "store_true", dest="auto_exposure", default=False, help="Get data from camera using auto exposition mode (maximize signal vertically by adjusting the exposure)" )
        parser.add_argument("-F", "--force",action = "store_true", dest="force", default=False, help="Allows overwriting file" )
        return parser

    def do_something(self,args):
        if args.camera:
            getattr(self.Instance,'set_camera')(args.camera)
        if args.nb_frames:
            getattr(self.Instance,'set_nb_frames')(args.nb_frames)
        if args.exposure:
            getattr(self.Instance,'set_exposure')(args.exposure)
        if args.auto_exposure and args.filename:
            getattr(self.Instance,'enable_auto_exposure')()
            getattr(self.Instance,'get_data')()
            getattr(self.Instance,'save_data')(filename=args.filename,FORCE=args.force)
        elif args.filename:
            getattr(self.Instance,'get_data')()
            getattr(self.Instance,'save_data')(filename=args.filename,FORCE=args.force)

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
