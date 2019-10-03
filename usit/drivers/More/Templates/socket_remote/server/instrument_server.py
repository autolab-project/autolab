#!/c/Python27/python.exe              # You might have to modify this line to your Operating System
# -*- coding: utf-8 -*-
"""


"""
import visa
import os
import time
import numpy

ADDRESS = 'TCPIP::192.168.0.3::INSTR'

class Driver():
    def __init__(self,address=ADDRESS):
        
        ### Initiate a connection to something, e.g. here using visa ###
        rm = v.ResourceManager()
        self.inst = rm.get_instrument(address)
        
        
    def command(self,command):
        if command == 'QUERY?':
            rep = self.idn()
            return rep
        elif command.startswith('ARGUMENT='):
            argument = float(command.split('=')[1])
            self.set_argument(argument)

    def set_argument(self,argument):
        self.inst.write('VOLT '+ argument)
    
    def idn():
        self.inst.write('*IDN?')
        return self.inst.read()
