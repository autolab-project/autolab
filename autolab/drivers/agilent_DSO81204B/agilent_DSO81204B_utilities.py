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

----------------  Extra infos:  ----------------
    - Datas are obtained in a binary format: int8 
    - Header is composed as follow:
    <format>, <type>, <points>, <count> , <X increment>, <X origin>, < X reference>, <Y increment>, <Y origin>, <Y reference>, <coupling>, <X display range>, <X display origin>, <Y display range>, <Y display origin>, <date>,
    <time>, <frame model #>, <acquisition mode>, <completion>, <X units>, <Y units>, <max bandwidth limit>, <min bandwidth limit>    
    - To retrieve datas (in "Units")
    Y-axis Units = data value * Yincrement + Yorigin (analog channels) 
    X-axis Units = data index * Xincrement + Xorigin

----------------  Examples:  ----------------

usage:    autolab driver [options] args 
        
    autolab driver -D {self.name} -A 192.168.0.3 -C VXI11 -o my_output_file -c 1
    Results in saving two files for the temporal trace of channel 1, the data and the scope parameters, called respectively my_output_file_DSACHAN1 and my_output_file_DSACHAN1.log
    
    autolab driver -D nickname -o my_output_file -c 1,2
    Same as previous one but with 4 output files, two for each channel (1 and 2) and using the device nickname as defined in local_config.ini
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-o", "--filename", type=str, dest="filename", default=None, help="Set the name of the output file" )
        parser.add_argument("-m", "--measure", type=str, dest="measure", default=None, help="Set measurment number" )
        parser.add_argument("-F", "--force",action="store_true", dest="force", default=None, help="Allows overwriting file" )
        parser.add_argument("-t", "--trigger", dest="trigger",action="store_true", help="Trigger the scope once" )
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
  

    def exit(self):
        self.Instance.close()
