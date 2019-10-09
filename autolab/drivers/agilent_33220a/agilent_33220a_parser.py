#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import agilent_33220a
from argparse import ArgumentParser
from functools import partial
import test


usage = """usage: %prog [options] arg
            
            
            EXAMPLES:
                
            

            """
parser = ArgumentParser(usage)


parser.add_argument("-c", "--command", nargs='+', dest="command", default=None, help="Set the command to use." )
parser.add_argument("-q", "--query", type=str, dest="query", default=None, help="Set the query to use." )


parser.add_argument("-r", "--ramp", type=float, dest="ramp", default=None, help="Turn on ramp mode." )
parser.add_argument("-o", "--offset", type=str, dest="offset", default=None, help="Set the offset value." )
parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the amplitude." )
parser.add_argument("-f", "--frequency", type=str, dest="frequency", default=None, help="Set the frequency." )

args = parser.parse_args()
#args = vars(parser.parse_args())


### Start the talker ###
classes_list = test.list_classes(agilent_33220a)
Driver_LINK  = test.identify_device_class(agilent_33220a,classes_list,args.link)
I = Driver_LINK(address=args.address)
methods_list = test.list_methods(I)

test.print_help_classes(classes_list)                  # display list of classes in module
test.print_help_methods(methods_list)                  # display list of methods in module
test.print_help_methods_arguments(I,methods_list)      # display list of methods arguments

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
    #message = test.parse_commands(I,commands,methods_list)
    for command in commands:
        print()
        print(f'Executing command:  {command}')
        message = None
        com     = command[0]
        assert com in methods_list, "Method not known or bound"
        coms = com.split('.')
        coms1_attr     = getattr(I,coms[1])
        
        NAME = None
        if len(coms)==2: NAME = partial(coms1_attr)
        else: coms1_attr_attr=getattr(coms1_attr,coms[-1]); NAME = partial(coms1_attr_attr)
        for k in range(len(command[1:])):
            is_there_equal = command[1+k].split('=')
            if len(coms)==2:
                if len(is_there_equal)==2:
                    if isinstance(is_there_equal[1],str):
                        exec(f'NAME = partial(NAME,{is_there_equal[0]}="{is_there_equal[1]}")')
                    else:
                        exec(f'NAME = partial(NAME,{is_there_equal[0]}={is_there_equal[1]})')
                else:
                    NAME = partial(NAME,is_there_equal[0])
            else:
                coms1_attr_attr = getattr(coms1_attr,coms[-1])
                if len(is_there_equal)==2:
                    if isinstance(is_there_equal[1],str):
                        exec(f'NAME = partial(NAME,{is_there_equal[0]}="{is_there_equal[1]}")')
                    else:
                        exec(f'NAME = partial(NAME,{is_there_equal[0]}={is_there_equal[1]})')
                else:
                    NAME = partial(NAME,is_there_equal[0])
        message = NAME()
        if message: print('Return:  ',message)
    print()

#I.close()
#sys.exit()
