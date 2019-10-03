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


if __name__=='__main__':

    usage = """usage: %prog [options] arg

               EXAMPLES:

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="command", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="query", default=None, help="Set the query to use." )
    parser.add_option("-i", "--address", type="string", dest="address", default=ADDRESS, help="Set the address to use for the communication" )
    parser.add_option("-a", "--argument", type="int", dest="argument", default=1, help="An argument" )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    I = Driver(address=options.address)
    
    if options.query:
        print('\nAnswer to query:',options.query)
        rep = I.query(options.query)
        print(rep,'\n')
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
    
    if options.argument:
        I.set_argument(options.argument)
        
    I.close()
    sys.exit()
