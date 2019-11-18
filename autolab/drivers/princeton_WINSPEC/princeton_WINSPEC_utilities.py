#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Spectrometer software'

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
            
    autolab driver -D {self.name} -C SOCKET -A 192.168.0.2 -e 0.1 -o my_file_name
    load {self.name} driver using SOCKET communication protocol with address 192.168.0.2 and acquire data after 2 expositions of 0.1s each. Save those into my_file_name.txt.
    
    autolab driver -D nickname -a -o my_file_name
    Similar to previous one using device's nickname defined in local_config.ini, turn on auto vertical scale/exposure optimization loop (so as to maximize signal vertically), get and save the data.
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-e", "--exposure", type=str, dest="exposure", default=None, help="Set the exposure time in s")
        parser.add_argument("-o", "--filename", type=str, dest="filename", default=None, help="Set the name of the output file")
        parser.add_argument("-a", "--auto_exposure", action = "store_true", dest="auto_exposure", default=False, help="Get data from camera using auto exposition mode (maximize signal vertically by adjusting the exposure)")
        parser.add_argument("-F", "--force",action = "store_true", dest="force", default=False, help="Allows overwriting file")
        
        return parser

    def do_something(self,args):
        if args.exposure:
            getattr(self.Instance,'setExposureTime')(args.exposure)
        if args.auto_exposure:
            getattr(self.Instance,'setAutoExposureTimeEnabled')(True)
        if args.filename:
            getattr(self.Instance,'acquireSpectrum')()
            data = getattr(self.Instance,'data')['spectrum']
            temp_filename = f'{filename}_WINSPEC.txt'
            if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(args.force):
                print(f'\nFile {temp_filename} already exists, change filename or remove old file\n')
                return
            f = savetxt(data)
            print('WINSPEC data saved')
        

    def exit(self):
        self.Instance.close()

