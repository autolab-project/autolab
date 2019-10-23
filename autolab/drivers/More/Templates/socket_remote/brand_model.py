#!/usr/bin/env python3

from optparse import OptionParser
import sys,os
import connector

ADDRESS = '192.168.0.2'

class Driver(connector.InstrumentConnectorRemote):
    def __init__(self,address=ADDRESS):
        
        ### Start the communication using socket ###
        connector.InstrumentConnectorRemote.__init__(self,address)
        
    def set_argument(self,argument):
        self.write('ARGUMENT='+str(argument))
        
    def get_query(self):
        return self.query('QUERY?')
