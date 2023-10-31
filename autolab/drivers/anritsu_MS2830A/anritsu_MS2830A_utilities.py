#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Spectrum Analyzer'

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
    autolab driver -D {self.name} -A GPIB0::2::INSTR -C VISA -m some_methods
    Execute some_methods of the driver. A list of available methods is present at the top of this help.

    autolab driver -D nickname -m some_methods
    Same as before using the nickname defined in local_config.ini
            """
        return usage

    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        # TODO: test if work
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the center frenqency in GHz." )
        parser.add_argument("-p1", "--power1",action=None, dest="power1", default=None, help="Power in dBm of the marker 1" )
        parser.add_argument("-p2", "--power2",action=None, dest="power2", default=None, help="Power in dBm of the marker 2" )

        return parser

    def do_something(self,args):
        #if args.filename:
            ##getattr(self.Instance,'get_data_traces')(traces=args.channels,single=args.trigger)
            #getattr(self.Instance,'get_data_traces')(traces=args.channels)
            #getattr(self.Instance,'save_data_traces')(filename=args.filename,traces=args.channels,FORCE=args.force)
        pass

    def exit(self):
        self.Instance.close()
