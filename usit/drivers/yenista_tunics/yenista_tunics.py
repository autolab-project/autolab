#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified): Yenista Tunics.
- 
"""



class Device():
    
    def __init__(self,address):
        self.write('MW')
        
    def wait(self):
        self.getID() # Not fantastic but programming interface really basic
             
    def getID(self):
        return self.query('*IDN?')
    
    def setFrequency(self,value):
        self.write(f"F={value}")
        self.wait()
        
    def getFrequency(self):
        return self.query("F?")

    def setWavelength(self,value):
        self.write(f"L={value}")
        self.wait()
        
    def getWavelength(self):
        return self.query("L?")
    
    def setPower(self,value):
        self.write(f"P={float(value)}")
        if value == 0 : self.setOutput(False)
        else : 
            if self.getOutput() is False : self.setOutput(True)
        self.wait()
        
    def getPower(self):
        ans=self.query("P?")
        if ans == 'DISABLED' : return 0
        else : return ans
    
    def setIntensity(self,value):
        self.write(f"I={float(value)}")
        if value == 0 : self.setOutput(False)
        else :
            if self.getOutput() is False : self.setOutput(True)
        self.wait()
        
    def getIntensity(self):
        ans=self.query("I?")
        if isinstance(ans,str) is True and ans == 'DISABLED' : return 0
        else : return ans
        
    def setOutput(self,state):
        if state is True : self.write("ENABLE")
        else : self.write("DISABLE")
        self.wait()
        
    def getOutput(self):
        ans = self.query("P?")
        if ans == 'DISABLED' : return False
        else : return True
        
        
        
        
    def getMotorSpeed(self):
        return self.query("MOTOR_SPEED?")   
 
    
    def setMotorSpeed(self,value):  # from 1 to 100 nm/s
        self.write("MOTOR_SPEED={float(value)}")
        self.wait()


    def getDriverConfig(self):
        
        config = []

        config.append({'element':'variable','name':'wavelength','type':str,
                       'read':self.getWavelength,'write':self.setWavelength})
    
        config.append({'element':'variable','name':'frequency','type':str,
                       'read':self.getFrequency,'write':self.setFrequency})

        config.append({'element':'variable','name':'power','type':str,
                       'read':self.getPower,'write':self.setPower})

        config.append({'element':'variable','name':'intensity','type':str,
                       'read':self.getIntensity,'write':self.setIntensity})
    
        config.append({'element':'variable','name':'output','type':str,
                       'read':self.getOutput,'write':self.setOutput})

        config.append({'element':'variable','name':'motorSpeed','type':str,
                       'read':self.getMotorSpeed,'write':self.setMotorSpeed})
    
        return config



#################################################################################
############################## Connections classes ##############################
class Device_VISA(Device):
    def __init__(self, address=None, **kwargs):
        import visa    
        
        self.TIMEOUT = 15000 #ms
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.TIMEOUT
        
        Device.__init__(self, **kwargs)
    
    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\n')
        if '=' in result : result = result.split('=')[1]
        try : result = float(result)
        except: pass
        return result
    
    def write(self,command):
        self.controller.write(command)
    
    def read(self):
        return self.controller.read()


############################## Connections classes ##############################
#################################################################################
        
    
    
if __name__ == '__main__':
    from optparse import OptionParser
    import sys,os
    
    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_yenistatunics -i GPIB0::1::INSTR -a 30 -w 1550
                   set the pump current to 30 mA and the and the wavelength to 1550
                   
                   Note that you might provide only on out of current and power at a time (same thing applies to frequency and wavelength)
               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="command", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="query", default=None, help="Set the query to use." )
    parser.add_option("-a", "--current", type="str", dest="current", default=None, help="Set the pump current in mA." )
    parser.add_option("-p", "--power", type="str", dest="power", default=None, help="Set the output power in mW." )
    parser.add_option("-f", "--frequency", type="str", dest="frequency", default=None, help="Set the operating frequency in GHz." )
    parser.add_option("-w", "--wavelength", type="str", dest="wavelength", default=None, help="Set the operating wavelength in nm." )
    parser.add_option("-i", "--address", type="str", dest="address", default='GPIB0::23::INSTR', help="Set the GPIB address to use to communicate." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    I = Device(address=options.address)
    if options.query:
        print('\nAnswer to query:',options.query)
        rep = I.query(options.query)
        print(rep,'\n')
        try: sys.exit()
        except: os._exit(1)
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
        try: sys.exit()
        except: os._exit(1)
    
    assert not(options.current and options.power), "Please provide EITHER current OR power"
    if options.current or (options.current==0):
        I.setIntensity(options.current)
    elif options.power or (options.power==0):
        I.setPower(options.power)
    assert not(options.wavelength and options.frequency), "Please provide EITHER wavelength OR frequency"
    if options.wavelength:
        I.setWavelength(options.wavelength)
    elif options.frequency:
        I.setFrequency(options.frequency)

    try: sys.exit()
    except: os._exit(1)

