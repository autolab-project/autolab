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
            
    autolab driver -D {self.name} -C VXI11 -A 192.168.0.4 -f 1000000 -p 0 -o 0.5 -a 1 -d 10e-6 -c AB,EF
    load {self.name} driver using VXI11 and local network address 192.168.0.4 and sets the frequency to 1MHz and acts on outputs AB and EF to set the polarity to 0 the offset to 0.5V amplitude to 1V and the delay to 10e-6s.
    
    autolab driver -D nickname -f 80e6 -c A,B -a 0.5 
    Similar to previous one but using the device's nickname as defined in local_config.ini and only for channel A and B. This will act only on B for instance if you do precise only B as channel argument.
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
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


    def exit(self):
        self.Instance.close()

