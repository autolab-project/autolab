#!/usr/bin/env python3
# -*- coding: utf-8 -*-

category = 'Optical source'

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
            
    autolab driver -D {self.name} -C USB -w 1550.2 -p 10
    load {self.name} driver using USB communication protocol with preconfigured vendor and deviceID and set the wavelength to 1550.2nm and the piezo to 10%.
    
    autolab driver -D nickname -x 1550.2,1551.3,3
    Use now the device nickname as defined in local_config.ini and perform a wavelength scan from 1550.2nm to 1551.3nm at a velocity of 3nm/s. I no third argument specified will use the device's stored one.

    autolab driver -D nickname -r 10,30.3,3
    Use now the device nickname as defined in local_config.ini and perform a piezo scan from 10% to 30% with a total period of 3s. If no third argument specified will go as fast as possible.
            """
        return usage
    
    def add_parser_arguments(self,parser):
        """Add arguments to the parser passed as input"""
        parser.add_argument("-w", "--wavelength", type=str, dest="wavelength", default=None, help="Set the wavelength value." )
        parser.add_argument("-x", "--scan_wavelength", type=str, dest="scan_wavelength", default=None, help="Set the wavelength scan values and start a scan. Arguments are:  min,max,speed (1 is the start wavelength, 2 is the stop wavelength, 3 is the scan speed in nm/s)." )
        parser.add_argument("-p", "--piezo", type=str, dest="piezo", default=None, help="Set the voltage to apply to the piezo in percent." )
        parser.add_argument("-r", "--scan_piezo", type=str,dest="scan_piezo", default=None, help="Set the values for the piezo scan and start a scan. Arguments are: min,max,time_scan (1 is the piezo start value, 2 is the piezo stop value, 3 is the total scan period)." )
        
        return parser

    def do_something(self,args):
        if args.wavelength:
            getattr(self.Instance,'wavelength')(args.wavelength)
        if args.piezo:
            getattr(self.Instance,'set_piezo')(args.piezo)
        if args.scan_wavelength:
            scan_wavelength = args.scan_wavelength.split(',')
            if len(scan_wavelength) == 3:
                getattr(self.Instance,'set_scan_forward_velocity')(scan_wavelength[2])
                getattr(self.Instance,'set_scan_backward_velocity')(scan_wavelength[2])
            elif len(scan_wavelength)!=2:
                print('Please provide 2 or 3 values for the scan')
                sys.exit()
            getattr(self.Instance,'set_scan_start_wavelength')(scan_wavelength[0])
            getattr(self.Instance,'set_scan_stop_wavelength')(scan_wavelength[1])
            getattr(self.Instance,'start_scan_wavelength')()  # starts wavelength scan
            sys.exit()
        if args.scan_piezo:
            getattr(self.Instance,'ramp_scanpiezo')(args.scan_piezo.split(','))
            sys.exit()


    def exit(self):
        #self.Instance.close()
        pass
