#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    category = 'Function generator'
    
    def __init__(self):        
        pass
    
    def amplitude(self,amplitude):
        self.write('AMPL '+amplitude)
    def offset(self,offset):
        self.write('OFFS '+offset)
    def frequency(self,frequency):
        self.write('FREQ '+frequency)
    def phase(self,phase):
        self.write('PHSE '+phase)

    def idn(self):
        return self.query('*IDN?')
        
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'amplitude','type':float,'unit':'V','write':self.amplitude,'help':'Voltage amplitude.'})
        config.append({'element':'variable','name':'offset','type':float,'unit':'V','write':self.offset,'help':'Voltage offset'})
        config.append({'element':'variable','name':'phase','type':float,'write':self.phase,'help':'Phase'})
        config.append({'element':'variable','name':'frequency','type':float,'unit':'Hz','write':self.frequency,'help':'Output frequency'})
        return config


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::19::INSTR',**kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.inst = rm.get_instrument(address)
        
        Driver.__init__(self)
        
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
    def __init__(self,address=19,board_index=0,**kwargs):
        import Gpib
        
        self.inst = Gpib.Gpib(int(address),int(board_index))
        Driver.__init__(self)
    
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        return self.inst.read()
    def close(self):
        """WARNING: GPIB closing is automatic at sys.exit() doing it twice results in a gpib error"""
        Gpib.gpib.close(self.inst.id)
############################## Connections classes ##############################
#################################################################################

            
if __name__ == '__main__':
    from optparse import OptionParser
    import inspect
    import sys

    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_srsDS345 -i 19 -b 0 -f 1.4e6 -a 1.1VP -o 0.1 -p 0.1
                   set the frequency to 1.4 MHz with an amplitude of 1.1 V, an offset of 100 mV and a phase of 1 degree. The gpib address is set to 19 and the board number to 0.
               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="command", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="query", default=None, help="Set the query to use." )
    parser.add_option("-o", "--offset", type="str", dest="offset", default=None, help="Set the offset value." )
    parser.add_option("-a", "--amplitude", type="str", dest="amplitude", default=None, help="Set the amplitude. Note: The units can be VP(Vpp), VR (Vrms), or DB (dBm)." )
    parser.add_option("-f", "--frequency", type="str", dest="frequency", default=None, help="Set the frequency." )
    parser.add_option("-p", "--phase", type="str", dest="phase", default=None, help="Set the phase." )
    parser.add_option("-i", "--address", type='str', dest="address", default='19', help="Set the GPIB address to use to communicate." )
    parser.add_option("-b", "--board_index", type='str', dest="board_index", default='0', help="Set the GPIB address to use to communicate." )
    parser.add_option("-l", "--link", type="string", dest="link", default='GPIB', help="Set the connection type." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    classes = [name for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass) if obj.__module__ is __name__]
    assert 'Driver_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Driver_')])
    Driver_LINK = getattr(sys.modules[__name__],'Driver_'+options.link)
    I = Driver_LINK(address=options.address,board_index=options.board_index)
    
    if options.query:
        print('\nAnswer to query:',options.query)
        rep = I.query(options.query)
        print(rep,'\n')
        sys.exit()
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
        sys.exit()
    
    if options.amplitude:
        I.amplitude(options.amplitude)
    if options.offset:
        I.offset(options.offset)
    if options.frequency:
        I.frequency(options.frequency)
    if options.phase:
        I.phase(options.phase)
    
    sys.exit()

