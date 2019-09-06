#!/usr/bin/env python3

import vxi11 as v
from optparse import OptionParser
import sys
import commands as C
import time
from numpy import fromstring,int8,int16,float64,sign

IP = '169.254.166.206'

class VXI11():
    def __init__(self,query=None,command=None,host=IP):

        ### Initiate communication ###
        self.scope = v.Instrument(host)
        if query:
            print('\nAnswer to query:',query)
            rep = self.query(query)
            print(rep,'\n')
        elif command:
            print('\nExecuting command',command)
            self.scope.write(command)
            print('\n')
            
            
    self.scope.close()
    sys.exit()
        
    
    def query(self, cmd, nbytes=1000000):
        """Send command 'cmd' and read 'nbytes' bytes as answer."""
        self.write(cmd)
        r = self.read(nbytes)
        return r
    def read(self,nbytes=1000000):
        self.scope.read(nbytes)
    def write(self,cmd):
        self.scope.write(cmd)
        

if __name__ == '__main__':

    usage = """usage: %prog [options] arg

               EXAMPLES:
                  
               

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-i", "--ipadd", type="string", dest="ipadd", default=IP, help="Set ip address" )
    (options, args) = parser.parse_args()
    
    
    ### Start the talker ###
    VXI11(query=options.que,command=options.com,filename=options.filename,host=options.ipadd)
    
