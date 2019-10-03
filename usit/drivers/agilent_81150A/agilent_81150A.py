#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    category = 'Function generator'
    
    def __init__(self,nb_channels=2):
        
        self.nb_channels = int(nb_channels)
        
        for i in range(1,self.nb_channels+1):
            setattr(self,f'channel{i}',Channel(self,i))
        
    
    def idn(self):
        self.write('*IDN?')
        self.read()


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='TCPIP::192.168.0.3::INSTR', **kwargs):
        import visa as v
        
        rm        = v.ResourceManager()
        self.inst = rm.get_instrument(address)
        Driver.__init__(self, **kwargs)
        
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        rep = self.inst.read()
        return rep
    def close(self):
        self.write(':SYST:COMM:RLST LOC')
        #self.inst.close()
############################## Connections classes ##############################
#################################################################################

class Channel():
    def __init__(self,dev,channel):
        self.channel = int(channel)
        self.dev  = dev
        
    def amplitude(self,amplitude):
        self.dev.write(f':VOLT{self.channel} {amplitude}')
    def offset(self,offset):
        self.dev.write(f':VOLT{self.channel}:OFFS {offset}')
    def frequency(self,frequency):
        self.dev.write(f':FREQ{self.channel} {frequency}')
    def dc_mode(self,offset):
        self.dev.write(f':FUNC{self.channel} DC')
        self.offset(offset=offset)
    def arbitrary_mode(self,waveform,round_factor=4):
        assert len(waveform) <= 524288, "Don't overcome Sample max of 524288"
        waveform = ''.join([str(round(waveform[i],round_factor))+',' for i in range(len(waveform))])[:-1]
        self.dev.write(f'DATA{self.channel} VOLATILE,{waveform}')
    def pulse_mode(self,width=None,duty_cycle=None):
        assert not(duty_cycle and width), "Please provide either duty_cycle OR width"
        self.dev.write(f':FUNC{self.channel} PULS')
        if duty_cycle: self.dev.write(f':PULS:DCYC{self.channel} {width}')
        if width:      self.dev.write(f':PULS:WIDT{self.channel} {width}')
        

            
if __name__ == '__main__':
    from optparse import OptionParser
    import inspect
    import sys
    
    usage = """usage: %prog [options] arg
               
               
               EXAMPLES:
                   set_agilent81150A -a 1 -o 1 -f 50KHZ 1,2
                   set the frequency to 50 kHz, the amplitude to 1V, the offset to 1V for both channel 1 and 2

                   set_agilent81150A -p w10NS 1
                   set pulse mode to channel 1 with pulse width of 10NS (MS stands for microseconds)

                   set_agilent81150A -p d10 2
                   set pulse mode to channel 2 with duty cycle of 10 purcent
                   
               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="command", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="query", default=None, help="Set the query to use." )
    parser.add_option("-o", "--offset", type="str", dest="offset", default=None, help="Set the offset value." )
    parser.add_option("-d", "--dc", type="str", dest="dc", default=None, help="Set dc mode and associated offset." )
    parser.add_option("-p", "--pulsemode", type="str", dest="pulsemode", default=None, help="Set pulse mode and use argument as either the duty cycle or the pulse width depending on the first letter 'd' or 'w' (see examples)." )
    parser.add_option("-a", "--amplitude", type="str", dest="amplitude", default=None, help="Set the amplitude." )
    parser.add_option("-f", "--frequency", type="str", dest="frequency", default=None, help="Set the frequency; may be 50000 or 50KHZ" )
    parser.add_option("-i", "--address", type="str", dest="address", default='TCPIP::192.168.0.3::INSTR', help="Set the Ip address to use for communicate." )
    (options, args) = parser.parse_args()
    
    ### Compute channels to act on ###
    if (len(args) == 0) and (options.command is None) and (options.query is None):
        print('\nYou must provide at least one channel\n')
        sys.exit()
    elif (options.command is not None) or (options.query is not None):
        pass
    else:
        chan = args[0].split(',')
        print(chan)

    ### Start the talker ###
    I = Driver(address=options.address)
    if options.query:
        print('\nAnswer to query:',options.query)
        rep = I.query(options.query)
        print(rep,'\n')
        I.exit()
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
        I.exit()
    
    for i in xrange(len(chan)):
        if options.amplitude:
            I.amplitude(chan[i],options.amplitude)
        if options.offset:
            I.offset(chan[i],options.offset)
        if options.frequency:
            I.frequency(chan[i],options.frequency)
        if options.dc:
            I.dc_mode(chan[i],options.dc)
        if options.pulsemode:
            if options.pulsemode[0]=="d": I.pulse_mode(chan[i],duty_cycle=options.pulsemode[1:])
            elif options.pulsemode[0]=="w": I.pulse_mode(chan[i],width=options.pulsemode[1:])
            else: print("pulse mode argument must start with either 'd' or 'w'")

    I.close()
    I.exit()
