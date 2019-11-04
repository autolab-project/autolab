#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import newport_TLB6700 as MODULE
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
            
    autolab-drivers -D {MODULE.__name__} -C USB -w 1550.2 -p 10
    load {MODULE.__name__} driver using USB communication protocol with preconfigured vendor and deviceID and set the wavelength to 1550.2nm and the piezo to 10%.
    
    autolab-drivers -D nickname -x 1550.2,1551.3,3
    Use now the device nickname as defined in local_config.ini and perform a wavelength scan from 1550.2nm to 1551.3nm at a velocity of 3nm/s. I no third argument specified will use the device's stored one.

    autolab-drivers -D nickname -r 10,30.3,3
    Use now the device nickname as defined in local_config.ini and perform a piezo scan from 10% to 30% with a total period of 3s. I no third argument specified will go as fast as possible.
    
    autolab-drivers -D nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-w", "--wavelength", type=str, dest="wavelength", default=None, help="Set the wavelength value." )
        parser.add_argument("-x", "--scan_wavelength", type=str, dest="scan_wavelength", default=None, help="Set the wavelength scan values and start a scan. Arguments are:  min,max,speed (1 is the start wavelength, 2 is the stop wavelength, 3 is the scan speed in nm/s)." )
        parser.add_argument("-p", "--piezo", type=str, dest="piezo", default=None, help="Set the voltage to apply to the piezo in percent." )
        parser.add_argument("-r", "--scan_piezo", type=str,dest="scan_piezo", default=None, help="Set the values for the piezo scan and start a scan. Arguments are: min,max,time_scan (1 is the piezo start value, 2 is the piezo stop value, 3 is the total scan period)." )
        return parser

    def do_something(self,args):
        if args.wavelength:
            getattr(self.Instance,'wavelength')(args.wavelength)
        if args.piezo:
            getattr(self.Instance,'set_piezo')(args.piezo)
        if args.scan_wavelength:
            scan_wavelength = args.scan_wavelength.split(',')
            if len(scan_wavelength) == 3:
                getattr(self.Instance,'set_scan_forward_velocity')(scan_wavelength[2])
                getattr(self.Instance,'set_scan_backward_velocity')(scan_wavelength[2])
            elif len(scan_wavelength)!=2:
                print('Please provide 2 or 3 values for the scan')
                sys.exit()
            getattr(self.Instance,'set_scan_start_wavelength')(scan_wavelength[0])
            getattr(self.Instance,'set_scan_stop_wavelength')(scan_wavelength[1])
            getattr(self.Instance,'start_scan_wavelength')()  # starts wavelength scan
            sys.exit()
        if args.scan_piezo:
            getattr(self.Instance,'ramp_scanpiezo')(args.scan_piezo.split(','))
            sys.exit()

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
        #self.Instance.close()
        pass
