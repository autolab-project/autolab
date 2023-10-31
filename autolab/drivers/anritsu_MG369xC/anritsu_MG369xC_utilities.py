#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Signal Generator'

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

    autolab driver -D {self.name} -A TCPIP::192.168.0.3::INSTR -C VISA -m some_methods
    Execute some_methods of the driver. A list of available methods is present at the top of this help.

    autolab driver -D nickname -m some_methods
    Same as before using the nickname defined in local_config.ini
            """
        return usage

    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-f", "--frequency", type=float, dest="frquency", default=None, help="Set the frequency of the signal in GHz")
        parser.add_argument("-p", "--power", type=float, dest="power", default=None, help="Set the power in dBm'")
        parser.add_argument("-o", "--output", type=int, dest="output", default=None, help="Turn on/off the source'")

        return parser

    def do_something(self,args):
        #if args.filename:
            ##getattr(self.Instance,'get_data_traces')(traces=args.channels,single=args.trigger)
            #getattr(self.Instance,'get_data_traces')(traces=args.channels)
            #getattr(self.Instance,'save_data_traces')(filename=args.filename,traces=args.channels,FORCE=args.force)
        pass

    def exit(self):
        self.Instance.close()
