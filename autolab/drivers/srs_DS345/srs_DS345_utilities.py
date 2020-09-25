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
            
    autolab driver -D {self.name} -A TCPIP::192.168.0.4::INSTR -C VISA -a 0.5VP -f 500 -p 1 -o 0.2
    load {self.name} driver using VISA communication protocol with address TCPIP... and set the amplitude to 0.5Volts peak to peak (see help on function -a for other available units), the frequency to 500Hz, the phase to 1 degree and the offset to 0.2V.
    
    autolab driver -D nickname -a 0.5 -f 500
    Similar to previous one but using the device's nickname as defined in local_config.ini
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-p", "--phase", type=str, dest="phase", default=None, help="Set the phase value in degree." )
        parser.add_argument("-o", "--offset", type=str, dest="offset", default=None, help="Set the offset value in Volts." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude. Note: The units can be VP(Vpp), VR (Vrms), or DB (dBm)." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency in Hz." )
        
        return parser

    def do_something(self,args):
        if args.amplitude:
            getattr(self.Instance,'amplitude')(args.amplitude)
        if args.offset:
            getattr(self.Instance,'offset')(args.offset)
        if args.frequency:
            getattr(self.Instance,'frequency')(args.frequency)
        if args.phase:
            getattr(self.Instance,'phase')(args.phase)
            

    def exit(self):
        self.Instance.close()

