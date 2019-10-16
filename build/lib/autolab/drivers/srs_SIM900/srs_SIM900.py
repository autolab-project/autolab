#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WARNING: The message processing to submodules is not optimal as connecting/disconnecting streams for each commands: should be optimized. See methods send_command_to_slot and get_query_from_slot of the Driver class.

Supported instruments (identified):
- 

"""

import time


class Driver():
    
    category = 'Electrical frame'
    slotNaming = 'slot<NUM> = <MODULE_NAME>,<SLOT_NAME>'
    
    def __init__(self, **kwargs):
        
        #self.write('CEOI ON')
        #self.write('EOIX ON')
        #self.write('TERM LF')
        
        # Submodules
        self.slotnames = []
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                print(key)
                module = globals()[ 'Module_'+kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                setattr(self,name,module(self,slot_num))
                self.slotnames.append(name)
        
    
    def send_command_to_slot(self,slot,command):
        self.write(f'CONN {slot},"CONAME"')
        self.write(command)
        self.write("CONAME")
    def get_query_from_slot(self,slot,command):
        self.write(f'CONN {slot},"CONAME"')
        rep = self.query(command)
        self.write("CONAME")
        return rep

    def idn(self):
        return self.query('*IDN?')

#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        import visa
        
        #rm = visa.ResourceManager()
        #self.inst = rm.get_instrument(address)
        
        Driver.__init__(self, **kwargs)
        
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
    
class Driver_GPIB(Driver):
    def __init__(self,address=2,board_index=0,**kwargs):
        import Gpib
        
        self.inst = Gpib.Gpib(int(address),int(board_index))
        Driver.__init__(self, **kwargs)
    
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
    
    category = 'PID controller'
    
    def __init__(self,dev,slot):
        self.slot = int(slot)
        self.dev  = dev
        

    def set_output_manual(self):
        self.dev.send_command_to_slot(self.slot,'AMAN 0')
    def set_output_pid(self):
        self.dev.send_command_to_slot(self.slot,'AMAN 1')
    def set_output_manual_voltage(self):
        self.dev.send_command_to_slot(self.slot,f'MOUT {val}')
    def get_output_voltage(self):
        return float(self.dev.get_query_from_slot(self.slot,'OMON?'))

    def auto_lock(self,peculiar=False):
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

    parser.add_option("-a", "--auto_lock", action = "store_true", dest="auto_lock", default=False, help="Enable auto locking." )
    parser.add_option("-l", "--lock", type="str", dest="lock", default=None, help="Lock" )
    parser.add_option("-u", "--unlock", type="str", dest="unlock", default=None, help="Unlock" )
    parser.add_option("-i", "--port", type="str", dest="port", default='5', help="Port for the PID frame to apply the command to" )
    parser.add_option("-s", "--setpoint", type="str", dest="setpoint", default=None, help="Setpoint value to be used" )


    (options, args) = parser.parse_args()
    

    if lock:
        self.write('AMAN 1')
    elif unlock:
        self.write('AMAN 0')
    if auto_lock:
        self.smart_relock(port)
    if re_lock:
        self.re_lock(port)
    if setpoint:
        self.write('SETP '+setpoint)
    
    I.close()
    sys.exit()
