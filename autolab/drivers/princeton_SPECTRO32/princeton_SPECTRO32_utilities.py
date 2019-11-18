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
            
    autolab driver -D {self.name} -C SOCKET -A 192.168.0.2 -c Camera1 -n 2 -e 0.1 -o my_file_name
    load {self.name} driver using SOCKET communication protocol with address 192.168.0.2 and acquire data from Camera1 after 2 expositions of 0.1s each. Save those into my_file_name.txt.
    
    autolab driver -D nickname -a -c Camera1 -o my_file_name
    Similar to previous one using device's nickname defined in local_config.ini, get and save the data using auto vertical scale/exposure optimization loop (so as to maximize signal vertically).
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-c", "--camera", type=str, dest="camera", default=None, help="Set the camera to get the data from." )
        parser.add_argument("-n", "--nb_frames", type=str, dest="nb_frames", default=None, help="Set the number of frames to acquire" )
        parser.add_argument("-e", "--exposure", type=str, dest="exposure", default=None, help="Set the exposure time in s" )
        parser.add_argument("-o", "--filename", type=str, dest="filename", default=None, help="Set the name of the output file" )
        parser.add_argument("-a", "--auto_exposure", action = "store_true", dest="auto_exposure", default=False, help="Get data from camera using auto exposition mode (maximize signal vertically by adjusting the exposure)" )
        parser.add_argument("-F", "--force",action = "store_true", dest="force", default=False, help="Allows overwriting file" )
        return parser

    def do_something(self,args):
        if args.camera:
            getattr(self.Instance,'set_camera')(args.camera)
        if args.nb_frames:
            getattr(self.Instance,'set_nb_frames')(args.nb_frames)
        if args.exposure:
            getattr(self.Instance,'set_exposure')(args.exposure)
        if args.auto_exposure and args.filename:
            getattr(self.Instance,'enable_auto_exposure')()
            getattr(self.Instance,'get_data')()
            getattr(self.Instance,'save_data')(filename=args.filename,FORCE=args.force)
        elif args.filename:
            getattr(self.Instance,'get_data')()
            getattr(self.Instance,'save_data')(filename=args.filename,FORCE=args.force)


    def exit(self):
        self.Instance.close()

