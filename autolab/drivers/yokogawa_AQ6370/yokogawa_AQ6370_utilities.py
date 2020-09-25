#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Spectrum analyser'
    
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
        
    autolab driver -D {self.name} -C SOCKET -A 192.168.0.9 -o my_output_file -c A,C
    Results in saving one file for the trace A, the data as seen on the scope and acquire ascii traces A and C in two different files my_output_file_AQ6370TRA.txt (and _AQ6370TRC.txt).
    
    autolab driver -D nickname -o my_output_file -c A,B,C
    Same as previous one but with 3 output files on per trace (A, B and C) and using the device nickname as defined in local_config.ini
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the traces to act on/acquire from." )
        parser.add_argument("-o", "--filename", type=str, dest="filename", default=None, help="Set the name of the output file" )
        parser.add_argument("-F", "--force",action="store_true", dest="force", default=None, help="Allows overwriting file" )
        parser.add_argument("-t", "--trigger",action="store_true", dest="trigger",default=False, help="Trigger the scope once" )
        
        return parser

    def do_something(self,args):
        if args.trigger and not args.filename:
            getattr(self.Instance,'single')()
        if args.filename:
            getattr(self.Instance,'get_data_traces')(traces=args.channels.split(','),single=args.trigger)
            getattr(self.Instance,'save_data_traces')(filename=args.filename,traces=args.channels.split(','),FORCE=args.force)
  

    def exit(self):
        self.Instance.close()
