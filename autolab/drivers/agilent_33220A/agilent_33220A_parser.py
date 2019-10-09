#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import agilent_33220A
from argparse import ArgumentParser
from functools import partial

class Driver_parser():
    def __init__(args,utilities):
        usage = """usage: %prog [options] arg
                    
                    
                    EXAMPLES:
                        
                    

                    """
        parser = ArgumentParser(usage=usage,parents=args)


        parser.add_argument("-c", "--command", nargs='+', dest="command", default=None, help="Set the command to use." )
        parser.add_argument("-q", "--query", type=str, dest="query", default=None, help="Set the query to use." )
        parser.add_argument("-r", "--ramp", type=float, dest="ramp", default=None, help="Turn on ramp mode." )
        parser.add_argument("-o", "--offset", type=str, dest="offset", default=None, help="Set the offset value." )
        parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude." )
        parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency." )
        parser.add_argument("-l", "--link", type=str, dest="link", default='VISA', help="Set the link to use for the connection." )
        parser.add_argument("-i", "--address", type=str, dest="address", default='192.168.0.2', help="Set the address to use for the communication." )

        args = parser.parse_args()
        #args = vars(parser.parse_args())


        ### Start the talker ###
        classes_list = utilities.list_classes(agilent_33220A)
        Driver_LINK  = utilities.identify_device_class(agilent_33220A,classes_list,args.link)
        I = Driver_LINK(address=args.address)
        methods_list = utilities.list_methods(I)

        utilities.print_help_classes(classes_list)                  # display list of classes in module
        utilities.print_help_methods(methods_list)                  # display list of methods in module
        utilities.print_help_methods_arguments(I,methods_list)      # display list of methods arguments

        if args.amplitude:
            I.amplitude(args.amplitude)
        if args.offset:
            I.offset(args.offset)
        if args.frequency:
            I.frequency(args.frequency)
        if args.ramp:
            I.ramp(args.ramp)

        if args.command:
            commands = [args.command[i].split(',') for i in range(len(args.command))]
            message = utilities.parse_commands(I,commands,methods_list)
            
        #I.close()
        #sys.exit()
