# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""
import visa

ADDRESS = 'ASRL15::INSTR'

class Device():
    
    def __init__(self,address=ADDRESS):
        
        self.DEF_TIMEOUT = 1000 #ms
        self.LONG_TIMEOUT = 5000 #ms
        self.BAUDRATE = 115200 
        
        # Angle configuration : 1=Closed  0=Open
        self.POS = {1:{1:30,0:60},
                    2:{1:125,0:85},
                    3:{1:25,0:70}}

        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.DEF_TIMEOUT
        self.controller.baud_rate = self.BAUDRATE
        
        self.config = '111' # default position ALL closed
        
        
        
        
        
        
    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\n')
        
        if '=' in result : result = result.split('=')[1]
        
        if 'SRV' in command : self.controller.timeout = self.LONG_TIMEOUT
        else : self.controller.timeout = self.DEF_TIMEOUT
        
        try : result = float(result)
        except: pass
    
        return result
    
    def write(self,command):
        self.controller.write(command)
        
        
    
    
    
        
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
        