#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import srs_DG645 as MODULE
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
            
    autolab-drivers -D {MODULE.__name__} -C VXI11 -A 192.168.0.4 -f 1000000 -p 0 -o 0.5 -a 1 -d 10e-6 -c AB,EF
    load {MODULE.__name__} driver using VXI11 and local network address 192.168.0.4 and sets the frequency to 1MHz and acts on outputs AB and EF to set the polarity to 0 the offset to 0.5V amplitude to 1V and the delay to 10e-6s.
    
    autolab-drivers -D nickname -f 80e6 -c A,B -a 0.5 
    Similar to previous one but using the device's nickname as defined in local_config.ini and only for channel A and B. This will act only on B for instance if you do precise only B as channel argument.
    
    autolab-drivers -D nickname -m some_methods1,arg1,arg2=23 some_methods2,arg1='test'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
            """
        parser = ArgumentParser(usage=usage,parents=[parser])
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency. This is applied to all of the outputs" )
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the channels to act on/acquire from. channels will be a list of outputs('AB','CD','EF','GH') or independant channels ('A','B','C','D','E','F','G','H'). WARNING: you can only change the relative delay between independant channels, you must act on outputs for other options. Pre-configured options only allow you to act on either outputs[single('AB') or several('AB','CD','GH')] or channels[single('A') or couple('A','B') only] with a single command => use several commands or -m option instead." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude.")
        parser.add_argument("-p", "--polarity", type=str, dest="polarity", default=None, help="Set the level polarity if 1, then up if 0, then down")
        parser.add_argument("-o", "--offset", type=str, dest="offset", default=None, help="Set the offset.")
        parser.add_argument("-d", "--delay", type=str, dest="delay", default=None, help="Set the delay (s).")
        
        return parser

    def do_something(self,args):
        if args.frequency:
            getattr(self.Instance,'set_frequency')(args.frequency)
        if args.delay and len(args.channels[0])==1:  # modify the delay for channels 'A','B,...'
            getattr(self.Instance,'set_delay_channels')(args.channels)
            getattr(self.Instance,'set_delay')(args.delay)
        elif args.channels:
            for out in args.channels.split(','):
                if args.amplitude:
                    getattr(getattr(self.Instance,f'output{out}'),'set_amplitude')(args.amplitude)
                if args.polarity:
                    getattr(getattr(self.Instance,f'output{out}'),'set_polarity')(args.polarity)
                if args.offset:
                    getattr(getattr(self.Instance,f'output{out}'),'set_offset')(args.offset)
                if args.delay:
                    getattr(getattr(self.Instance,f'output{out}'),'set_delay')(args.delay)

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
