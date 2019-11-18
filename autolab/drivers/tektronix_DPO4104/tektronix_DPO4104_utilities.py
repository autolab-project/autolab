#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Oscilloscope'
    
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
        
    autolab driver -D {self.name} -A 192.168.0.3 -C VXI11 -o my_output_file -c 1
    Results in saving two files for the temporal trace of channel 1, the data and the scope parameters, called respectively my_output_file_DPO4104CH1 and my_output_file_DPO4104CH1.log
    
    autolab driver -D nickname -o my_output_file -F -c 1,2
    Same as previous one but with 4 output files, two for each channel (1 and 2) and using the device nickname as defined in local_config.ini. If files with your filename already exist -F flag overwrite them.
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-o", "--filename", type=str, dest="filename", default=None, help="Set the name of the output file" )
        parser.add_argument("-F", "--force",action="store_true", dest="force", default=None, help="Allows overwriting file" )
        
        return parser

    def do_something(self,args):
        if args.filename:
            getattr(self.Instance,'get_data_channels')(channels=args.channels.split(','))
            getattr(self.Instance,'save_data_channels')(filename=args.filename,channels=args.channels.split(','),FORCE=args.force)


    def exit(self):
        self.Instance.close()

