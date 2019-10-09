#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inspect
from functools import partial

#usitconfig.checkConfig()
#usitconfig.DEVICES_INDEX_PATH

def print_help_classes(classes_list):
    print()
    print(f'[Classes]\n{", ".join(classes_list)}')
def print_help_methods(methods_list):
    print()
    print(f'[Methods]\n{", ".join(methods_list)}')
def print_help_methods_arguments(I,methods_list):
    print()
    print(f'[Methods arguments]')
    for command in methods_list:
        com = command
        coms = com.split('.')
        coms1_attr = getattr(I,coms[1])
        if len(coms)==2: print(f'{command}   ',inspect.signature(coms1_attr))
        else: print(f'{command}  ',inspect.signature(getattr(coms1_attr,coms[-1]))) 
    
def list_classes(module):
    return [name for name, obj in inspect.getmembers(module, inspect.isclass) if obj.__module__ is module.__name__]
def list_methods(I):
    methods_list = []
    class_meth = [f'I.{name}' for name,obj in inspect.getmembers(I,inspect.ismethod) if name != '__init__']
    class_vars = [f'I.{key}.{name}' for key in vars(I).keys() for name,obj in inspect.getmembers(vars(I)[key],inspect.ismethod) if inspect.getmembers(vars(I)[key],inspect.ismethod) != '__init__' and inspect.getmembers(vars(I)[key],inspect.ismethod) and name!='__init__']
    methods_list.extend(class_meth);methods_list.extend(class_vars)
    return methods_list
    
def identify_device_class(module,classes_list,link):
    assert 'Driver_'+link in classes_list , "Not in " + str([a for a in classes_list if a.startwith('Driver_')])
    Driver_LINK = getattr(module,'Driver_'+link)
    return Driver_LINK

def parse_commands(I,commands,methods_list):
    global NAME   # necessary for exec function
    
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
                        exec(f'NAME = partial(NAME,{is_there_equal[0]}="{is_there_equal[1]}")',globals())
                    else:
                        exec(f'NAME = partial(NAME,{is_there_equal[0]}={is_there_equal[1]})',globals())
                else:
                    NAME = partial(NAME,is_there_equal[0])
            else:
                coms1_attr_attr = getattr(coms1_attr,coms[-1])
                if len(is_there_equal)==2:
                    if isinstance(is_there_equal[1],str):
                        exec(f'NAME = partial(NAME,{is_there_equal[0]}="{is_there_equal[1]}")',globals())
                    else:
                        exec(f'NAME = partial(NAME,{is_there_equal[0]}={is_there_equal[1]})',globals())
                else:
                    NAME = partial(NAME,is_there_equal[0])
        message = NAME()
        if message: print('Return:  ',message)
    print()

