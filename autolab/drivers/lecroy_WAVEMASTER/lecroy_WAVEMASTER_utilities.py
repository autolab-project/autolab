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
    - To retrieve datas (in "VERTUNIT"), see corresponding log file:
    DATA(VERTUNIT) = DATA(ACQUIRED) * VERTICAL_GAIN - VERTICAL_OFFSET

----------------  Examples:  ----------------

usage:    autolab driver [options] args
        
    autolab driver -D {self.name} -A 192.168.0.3 -C VXI11 -o my_output_file -c 1,2
    Results in saving two files for the trace 1, the data and the scope parameters, called respectively my_output_file_DSACHAN1 and my_output_file_DSACHAN1.log
    
    autolab driver -D nickname -o my_output_file -f WORD 
    Same as previous will save all channels as None are specified and using the device nickname as defined in local_config.ini. the encoding is set to WORD
    
    autolab driver -D nickname -o my_output_file -a 1,3 -b 8
    Vertical autoscale will be enabled for channels 1 and 3. They will both go through the optimization loop 5 times, and aiming 8 vertical divisions.
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-c", "--channels", type=str, dest="channels", default=None, help="Set the channels to act on/acquire from." )
        parser.add_argument("-o", "--filename", type=str, dest="filename", default=None, help="Set the name of the output file" )
        parser.add_argument("-F", "--force",action="store_true", dest="force", default=None, help="Allows overwriting file" )
        parser.add_argument("-t", "--trigger", dest="trigger",action="store_true", help="Trigger the scope once" )
        parser.add_argument("-f", "--format", type=str, dest="format", default=None, help="Change data encoding" )
        parser.add_argument("-a", "--auto_scale", type=str, dest="auto_scale", default=None, help="To allow auto modification of the vertical gain. Argument is a list of all the channels to apply spe mode to. Note if no channel specified. Note: it will work best if your scope triggers (i.e. not on AUTO trigger mode with no relevant trigger signal). WARNING: Specifying more than one channel to apply auto_scale to will result in different trigger events for the acquired channels.")
        parser.add_argument("-b", "--auto_fact", type=float, dest="auto_fact", default=None, help="For setting limits of the vertical gain, units are in number of scope divisions here. WARNING: code security avoid traces too close from screen extrema (at 9 divisions) and result in endless looping. WARNING: the number of vertical divisions might depend on the scope (8 or 10 usually)." )

        return parser

    def do_something(self,args):
        if args.format:
            getattr(self.Instance,'set_encoding')(args.format)
        if args.trigger and not args.filename:
            getattr(self.Instance,'single')()
        if args.auto_scale: # test must be located before args.filename's one
            for chan in args.auto_scale.split(','):
                getattr(getattr(self.Instance,f'channel{chan}'),'set_autoscale_enable')()
        if args.auto_fact: # test must be located before args.filename's one
            for chan in range(1,getattr(self.Instance,'nb_channels')+1):
                getattr(getattr(self.Instance,f'channel{chan}'),'set_autoscale_factor')(args.auto_fact) # all channels instances
        if args.filename:
            acq_channels = args.channels.split(',')
            if args.auto_scale:      # Sort channels for auto ones to be acquired first
                for chan_auto in args.auto_scale.split(','):
                    if chan_auto in acq_channels:
                        acq_channels.remove(chan_auto)
                        acq_channels.insert(0,chan_auto)
            getattr(self.Instance,'get_data_channels')(channels=acq_channels,single=args.trigger)
            getattr(self.Instance,'save_data_channels')(filename=args.filename,channels=acq_channels,FORCE=args.force)
  

    def exit(self):
        self.Instance.close()
        
        
