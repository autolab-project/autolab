#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


        
    

class Device():
    
    def __init__(self):
        

        
        # Angle configuration : 1=Closed  0=Open
        self.POS = {1:{1:30,0:60},
                    2:{1:125,0:85},
                    3:{1:25,0:70}}
        
        self.config = '111' # default position ALL closed



    def getID(self):
        return self.query('*IDN?')
    


    def setSafeState(self):
        self.setConfig('111')
        if self.getConfig() == '111' :
            return True
        
        
        
    def setConfig(self,value):
        assert isinstance(value,str)
        assert len(value) == 3
        
        command = ''
        for i in range(3):
            try :
                servoID = i+1
                position = self.shutterPositions[servoID][int(value[i])]
                command+=f'SRV{servoID}={position},'
            except :
                pass

        self.query(command)

        self.config = value
        
    
    def getConfig(self):
        return self.config
    
    
 
    def invertConfig(self):
        newConfig = ''
        for i in range(3):
            try :
                newConfig += str(int(not bool(int(self.config[i]))))
            except :
                newConfig += 'x'
        self.setConfig(newConfig)
        
      
        
    def setAngleShutter1(self,value):
        self.query(f'SRV1={value}')
        
    def setAngleShutter2(self,value):
        self.query(f'SRV2={value}')
        
    def setAngleShutter3(self,value):
        self.query(f'SRV3={value}')
        
    def getDriverConfig(self):
        
        config = []
        
        config.append({'element':'action','name':'closeAll','do':self.setSafeState,'help':'Close every shutters'})
        config.append({'element':'action','name':'invert','do':self.invertConfig,'help':'Invert every shutters state'})
        config.append({'element':'variable','name':'config','read':self.getConfig,'write':self.setConfig,'type':str,'help':'Shutter configuration. 1 is closed, 0 is opened.'})

        return config
  


#################################################################################
############################## Connections classes ##############################
class Device_VISA(Device):
    def __init__(self, address):
        import visa 
        
        self.DEF_TIMEOUT = 1000 #ms
        self.LONG_TIMEOUT = 5000 #ms
        self.BAUDRATE = 115200 
        
        # Instantiation
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(address)
        self.inst.timeout = self.DEF_TIMEOUT
        self.inst.baud_rate = self.BAUDRATE
        
        Device.__init__(self)
        
        
    def close(self):
        try : self.inst.close()
        except : pass

    def query(self,command):
        result = self.inst.query(command)
        result = result.strip('\n')
        
        if '=' in result : result = result.split('=')[1]
        
        if 'SRV' in command : self.inst.timeout = self.LONG_TIMEOUT
        else : self.inst.timeout = self.DEF_TIMEOUT
        
        try : result = float(result)
        except: pass
    
        return result
    
    def write(self,command):
        self.inst.write(command)

############################## Connections classes ##############################
#################################################################################
        
        
        
if __name__ == '__main__' : 
    ADDRESS = 'ASRL15::INSTR'
        