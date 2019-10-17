#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified): Yenista Tunics.
- 
"""


class Driver():
    
    category = 'Optical source'
    
    def __init__(self):
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

        config.append({'element':'variable','name':'wavelength','unit':'nm','type':float,
                       'read':self.getWavelength,'write':self.setWavelength})
    
        config.append({'element':'variable','name':'frequency','unit':'GHz','type':float,
                       'read':self.getFrequency,'write':self.setFrequency})

        config.append({'element':'variable','name':'power','unit':'mW','type':float,
                       'read':self.getPower,'write':self.setPower})

        config.append({'element':'variable','name':'intensity','unit':'mA','type':float,
                       'read':self.getIntensity,'write':self.setIntensity})
    
        config.append({'element':'variable','name':'output','type':bool,
                       'read':self.getOutput,'write':self.setOutput})

        config.append({'element':'variable','name':'motorSpeed','unit':'nm/s','type':float,
                       'read':self.getMotorSpeed,'write':self.setMotorSpeed})
    
        return config



#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR', **kwargs):
        import visa    
        
        self.TIMEOUT = 15000 #ms
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.TIMEOUT
        
        Driver.__init__(self)
    
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
        

