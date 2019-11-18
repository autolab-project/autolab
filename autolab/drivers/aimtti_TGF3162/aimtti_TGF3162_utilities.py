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
            
    autolab driver -D {self.name} -C SOCKET -A 192.168.0.8 -a 0.5 -f 80000000 -c 1,2
    load {self.name} driver using socket and set the channel 1 and 2 amplitude to 0.5V and frequency to 80MHz.
    
    autolab driver -D nickname -a 0.5 -f 80e6 -c 1
    same as before but using the device nickname as defined in local_config.ini and only for channel 1.
    
    Note: Arbitrary waveform available only using a python terminal
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency." )
        parser.add_argument("-p", "--period", type=str, dest="period", default=None, help="Set the period." )
        parser.add_argument("-n", "--set_mode", type=str, dest="set_mode", default=None, help="Switch to the requested mode. Accepted values are: SINE,SQUARE,RAMP,TRIANG,PULSE,NOISE,PRBSPN7,PRBSPN9,PRBSPN11,PRBSPN15,PRBSPN20,PRBSPN23,PRBSPN29,PRBSPN31 or ARB" )
        
        return parser

    def do_something(self,args):
        if args.channels:
            for chan in args.channels.split(','):
                if args.set_mode:
                    getattr(getattr(self.Instance,f'channel{chan}'),'set_mode')(args.set_mode)
                if args.amplitude:
                    getattr(getattr(self.Instance,f'channel{chan}'),'amplitude')(args.amplitude)
                if args.frequency:
                    getattr(getattr(self.Instance,f'channel{chan}'),'frequency')(args.frequency)
                if args.offset:
                    getattr(getattr(self.Instance,f'channel{chan}'),'offset')(args.offset)


    def exit(self):
        self.Instance.close()
