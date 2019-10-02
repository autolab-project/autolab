#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WARNING: The message processing to submodules is not optimal as connecting/disconnecting streams for each commands: should be optimized.

Supported instruments (identified):
- 

"""

import time


class Device():
    
    modules = {'Module_SIM960':Module_SIM960}
    slotNaming = 'slot<NUM> = <MODULE_NAME>,<SLOT_NAME>'
    
    def __init__(self):
        
        self.write('CEOI ON')
        self.write('EOIX ON')
        self.write('TERM LF')
        
        # Submodules
        self.slotnames = []
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = modules[ kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                setattr(self,name,module(self,slot_num))
                self.slotnames.append(name)
        
        
    def idn(self):
        return self.query('*IDN?')


#################################################################################
############################## Connections classes ##############################
class Device_VISA(Device):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.inst = rm.get_instrument(address)
        
        Device.__init__(self)
        
    def close(self):
        self.inst.close()
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        rep = self.inst.read()
        return rep
    
class Device_GPIB(Device):
    def __init__(self,address=2,board_index=0,**kwargs):
        import Gpib
        
        self.inst = Gpib.Gpib(int(address),int(board_index))
        Device.__init__(self)
    
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,command):
        self.inst.write(command)
    def read(self):
        return self.inst.read()
    def close(self):
        """WARNING: GPIB closing is automatic at sys.exit() doing it twice results in a gpib error"""
        Gpib.gpib.close(self.inst.id)
############################## Connections classes ##############################
#################################################################################


class Module_SIM960():
    def __init__(self,dev,slot):
        self.slot = int(slot)
        self.dev  = dev
        

    def send_command_to_slot(self,command):
        self.dev.write(f'CONN {self.slot},"CONAME"')
        self.dev.write(command)
        self.dev.write("CONAME")
    def get_query_from_slot(self,command):
        self.dev.write(f'CONN {self.slot},"CONAME"')
        rep = self.dev.query(command)
        self.dev.write("CONAME")
        return rep

    def set_output_manual(self):
        self.send_command_to_slot('AMAN 0')
    def set_output_pid(self):
        self.send_command_to_slot('AMAN 1')
    def set_output_manual_voltage(self,val):
        self.send_command_to_slot(f'MOUT {val}')
    def get_output_voltage(self):
        return float(self.get_query_from_slot('OMON?'))

    def smart_relock(self,peculiar=False):
        rep = self.get_output_voltage()
        if peculiar:                     # port 5
            if rep<1.5 or rep>8.5:
                self.re_lock()
        else:
            if rep<-3.5 or rep>3.5:
                self.re_lock(port)

                
    def re_lock(self):
        self.set_output_manual()
        time.sleep(0.1)
        if peculiar:                     # port 5
            self.set_output_manual_voltage(5)
        else:
            self.set_output_manual_voltage(0)
        time.sleep(0.1)
        self.set_output_pid()



if __name__ == '__main__':

    from optparse import OptionParser
    import inspect
    import sys

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
    parser.add_option("-t", "--testout", action = "store_true", dest="testout", default=False, help="Test the output voltage and re-lock if needed" )
    parser.add_option("-i", "--address", type="str", dest="address", default='2', help="Set gpib address to use for the communication" )
    parser.add_option("-b", "--board_index", type='str', dest="board_index", default='0', help="Set the GPIB address to use to communicate." )
    parser.add_option("-l", "--link", type="string", dest="link", default='GPIB', help="Set the connection type." )
    parser.add_option("-p", "--port", type="str", dest="port", default='5', help="Port for the PID frame to apply the command to" )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    classes = [name for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass) if obj.__module__ is __name__]
    assert 'Device_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Device_')])
    Device_LINK = getattr(sys.modules[__name__],'Device_'+options.link)
    I = Device_LINK(address=options.address,board_index=options.board_index)
    
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
    
    I.close()
    sys.exit()
