#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Power meter'

class Driver_parser():
    def __init__(self, Instance, name, **kwargs):
        self.name     = name
        self.Instance = Instance
        
        
    def add_parser_usage(self,message):
        """Usage to be used by the parser"""
        usage = rf"""
{message}

----------------  Examples:  ----------------

usage:    autolab driver [options] args
        
    autolab driver -D {self.name} -C DLL --port 'C:\Program Files\Newport\Newport USB Driver\Bin\usbdll.dll' -m some_methods
    In this particular case the --port option indicate the dll library location. Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition.
    
    autolab driver -D nickname -m some_methods
    same as before but using the device nickname as defined in local_config.ini
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        #parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the traces to act on/acquire from." )
        #parser.add_argument("-o", "--filename", type=str, dest="filename", default=None, help="Set the name of the output file" )
        #parser.add_argument("-F", "--force",action="store_true", dest="force", default=None, help="Allows overwriting file" )
        #parser.add_argument("-t", "--trigger", dest="trigger",action="store_true", help="Trigger the scope once" )
        
        return parser
    
    def do_something(self,args):
        #if args.filename:
            ##getattr(self.Instance,'get_data_traces')(traces=args.channels,single=args.trigger)
            #getattr(self.Instance,'get_data_traces')(traces=args.channels)
            #getattr(self.Instance,'save_data_traces')(filename=args.filename,traces=args.channels,FORCE=args.force)
  
        pass


    def exit(self):
        self.Instance.close()

