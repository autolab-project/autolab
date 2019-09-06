#!/usr/bin/env python3

"""

Python module made for controlling srs SIM960 (PID controller) inserted in a SIM900 frame 

"""

import visa as v
from optparse import OptionParser
import sys
import time

ADDRESS = 'GPIB::2::INSTR'

class Device():
        def __init__(self,address=ADDRESS,query=None,command=None,smart_relock=None,port=None,setpoint=None,auto_lock=None,lock=None,unlock=None):
            
            rm = v.ResourceManager('@py')
            self.PID = rm.get_instrument(address)
            self.PID.write('CEOI ON')
            self.PID.write('EOIX ON')
            
            self.write('CONN '+port+',"CONAME"')
            self.write('TERM LF')
            
            self.write('*IDN?')
            print('\nCONNECTING to module on PORT', port,':',self.read())
            
            if query:
                print('\nAnswer to query:',query)
                self.write(query)
                rep = self.read()
                print(rep,'\n')
                self.exit()
            elif command:
                print('\nExecuting command',command)
                self.write(command)
                print('\n')
                self.exit()
            
            if lock:
                self.write('AMAN 1')
            elif unlock:
                self.write('AMAN 0')
            if smart_relock:
                self.smart_relock(port)
            if auto_lock:
                self.re_lock(port)
            if setpoint:
                self.write('SETP '+setpoint)
            
            self.exit()
        
        
        def smart_relock(self,port):
            self.write('OMON?')
            rep = eval(self.read())
            if port=='3':
                if rep<-3.5 or rep>3.5:
                    self.re_lock(port)
            elif port=='5':
                if rep<1.5 or rep>8.5:
                    self.re_lock(port)
        def re_lock(self,port):
            self.write('AMAN 0')
            time.sleep(0.1)
            if port=='3':
                self.write('MOUT 0')
            elif port=='5':
                self.write('MOUT 5')
            time.sleep(0.1)
            self.write('AMAN 1')
        
        def exit(self):
            self.write('CONAME')
            sys.exit()
        def write(self,query):
            self.PID.write(query)
        def read(self):
            return self.PID.read()
            

if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_PIDSRS -i 5 -s 0.1
                   set the setpoint of the module plugged in the port 5 to 0.1


               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-a", "--autolock", action = "store_true", dest="autolock", default=False, help="Enable auto locking." )
    parser.add_option("-l", "--lock", type="str", dest="lock", default=None, help="Lock" )
    parser.add_option("-u", "--unlock", type="str", dest="unlock", default=None, help="Unlock" )
    parser.add_option("-i", "--port", type="str", dest="port", default='5', help="Port for the PID freme to apply the command to" )
    parser.add_option("-s", "--setpoint", type="str", dest="setpoint", default=None, help="Setpoint value to be used" )
    parser.add_option("-i", "--address", type="str", dest="address", default=ADDRESS, help="Set gpib address to use for the communication" )
    parser.add_option("-t", "--testout", action = "store_true", dest="testout", default=False, help="Test the output voltage and re-lock if needed" )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    Device(address=options.address,query=options.que,command=options.com,smart_relock=options.testout,port=options.port,setpoint=options.setpoint,auto_lock=options.autolock,lock=options.lock,unlock=options.unlock)
