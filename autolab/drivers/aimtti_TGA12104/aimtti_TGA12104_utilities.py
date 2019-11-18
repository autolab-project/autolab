#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Function generator'

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
            
    autolab driver -D {self.name} -C USB -a 0.5 -f 500 -c 1,2
    load {self.name} driver using pyusb and set the amplitude to 0.5V and frequency to 500Hz to channels 1 and 2.
    
    autolab driver -D nickname -a 0.5 -f 500 -c 1
    same as before but using the device nickname as defined in local_config.ini, only acting on channel 1
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency." )
        parser.add_argument("-p", "--period", type=str, dest="period", default=None, help="Set the period." )
        
        return parser

    def do_something(self,args):
        if args.channels:
            for chan in args.channels.split(','):
                if args.amplitude:
                    getattr(getattr(self.Instance,f'channel{chan}'),'amplitude')(args.amplitude)
                if args.frequency:
                    getattr(getattr(self.Instance,f'channel{chan}'),'frequency')(args.frequency)
                if args.period:
                    getattr(getattr(self.Instance,f'channel{chan}'),'period')(args.period)


    def exit(self):
        self.Instance.close()
