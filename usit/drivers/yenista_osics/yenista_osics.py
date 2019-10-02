#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

class Device():

    slotNaming = 'slot<NUM> = <MODULE_NAME>,<SLOT_NAME>'

    def __init__(self,**kwargs):
        
        self.write('*RST') # The input buffer is cleared. The command interpreter is reset and a reset instruction is sent to every module. The status and event registers are cleared. Sets the OPC bit to 1.
        self.write('*CLS') # Clears the Event Status Register and the output queue. Sets the OPC bit to 1.
        
        # Submodules loading
        self.slotnames = []
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = globals()[ 'Module_'+kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                setattr(self,name,module(self,slot_num))
                self.slotnames.append(name)


    def getID(self):
        return self.query('*IDN?')


    def getDriverConfig(self):
        config = []
        for name in self.slotnames :
            config.append({'element':'module','name':name,'object':getattr(self,name)})
        return config


#################################################################################
############################## Connections classes ##############################
class Device_VISA(Device):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        
        import visa
        
        
        self.TIMEOUT = 60000 #ms
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.TIMEOUT
        
        Device.__init__(self,**kwargs)
        

    def close(self):
        try : self.controller.close()
        except : pass


    def write(self,command):
        self.controller.write(command)
        
    def read(self):
        result = self.controller.read()
        result = result.strip('\n')
        return result
    
    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\n')
        return result
        
############################## Connections classes ##############################
#################################################################################


class Module_T100():   
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = slot
        self.prefix = f'CH{int(slot)}:'
        
        self.write(self.prefix+'NM')
        self.write(self.prefix+'MW')


    def write(self,command):
        self.dev.write(command)
        
    def read(self):
        return self.dev.read()
    
    def query(self,command):
        return self.dev.query(command)
    
    #--------------------------------------------------------------------------
    # Optional functions
    #--------------------------------------------------------------------------
    
    def setSafeState(self):
        self.setOutputState(False)
        if self.getOutputState() is False :
            return True
            

    def getID(self):
        result = self.query(self.prefix+'*IDN?')
        result = self.cleanResult(result)
        return result
        
        
    #--------------------------------------------------------------------------
    # Instrument variables
    #--------------------------------------------------------------------------
        
    def cleanResult(self,result):
        try:
            result=result.split(':')[1]
            result=result.split('=')[1]
            result=float(result)
        except:
            pass
        return result
    
    


    def setWavelength(self,value):
        self.write(self.prefix+f"L={value}")
        self.query('*OPC?')
        
    def getWavelength(self):
        result = self.query(self.prefix+'L?')
        result = self.cleanResult(result)
        return result
    
    
    
    
    
    def setFrequency(self,value):
        self.write(self.prefix+f"F={value}")
        self.query('*OPC?')
        
    def getFrequency(self):
        result = self.query(self.prefix+'F?')
        result = self.cleanResult(result)
        return result
    
    
    
    
    
    
    def setPower(self,value):
        if value == 0 :
            self.setOutputState(False)
        else :
            if self.getOutputState() is False :
                self.setOutputState(True)
            self.write(self.prefix+f"P={value}")
            self.query('*OPC?')
            
    def getPower(self):
        result = self.query(self.prefix+'P?')
        result = self.cleanResult(result)
        if result == 'Disabled':
            return 0
        else :
            return result
    




    
    def setIntensity(self,value):
        if value == 0 :
            self.setOutputState(False)
        else :
            if self.getOutputState() is False :
                self.setOutputState(True)
            self.write(self.prefix+f"I={value}")
            self.query('*OPC?')
        
    def getIntensity(self):
        result = self.query(self.prefix+'I?')
        result = self.cleanResult(result)
        if result == 'Disabled':
            return 0
        else :
            return result
        
        
    
    
    
    def setCoherenceControlState(self,state):
        if state is True :
            self.write(self.prefix+'CTRL ON')
        else :
            self.write(self.prefix+'CTRL OFF')
        self.query('*OPC?')
        
    def getCoherenceControlState(self):
        result = self.query(self.prefix+'CTRL?')
        result = self.cleanResult(result)
        return bool(int(result))
    
    
    
    
    def setAutoPeakFindControlState(self,state):
        if state is True :
            self.write(self.prefix+'APF ON')
        else :
            self.write(self.prefix+'APF OFF')
        self.query('*OPC?')
        
    def getAutoPeakFindControlState(self):
        result = self.query(self.prefix+'APF?')
        result = self.cleanResult(result)
        return bool(int(result))
    
    
    
    
    
    def setOutputState(self,state):
        if state is True :
            self.write(self.prefix+"ENABLE")
        else :
            self.write(self.prefix+"DISABLE")
        self.query('*OPC?')
        
    def getOutputState(self):
        result = self.query(self.prefix+'ENABLE?')
        result = self.cleanResult(result)
        return result == 'ENABLED'
    
    
    
    def getDriverConfig(self):
        
        config = []
        config.append({'element':'variable','name':'wavelength','type':float,'unit':'nm','read':self.getWavelength,'write':self.setWavelength,'help':'Wavelength'})
        config.append({'element':'variable','name':'frequency','type':float,'unit':'GHz','read':self.getFrequency,'write':self.setFrequency,'help':'Frequency'})
        config.append({'element':'variable','name':'power','type':float,'unit':'mW','read':self.getPower,'write':self.setPower,'help':'Output power'})
        config.append({'element':'variable','name':'intensity','type':float,'unit':'mA','read':self.getIntensity,'write':self.setIntensity,'help':'Current intensity'})
        config.append({'element':'variable','name':'output','type':bool,'read':self.getOutputState,'write':self.setOutputState,'help':'Output state'})
        config.append({'element':'variable','name':'coherenceControl','type':bool,'read':self.getCoherenceControlState,'write':self.setCoherenceControlState,'help':'Coherence control mode'})
        config.append({'element':'variable','name':'autoPeakFindControl','type':bool,'read':self.getAutoPeakFindControlState,'write':self.setAutoPeakFindControlState,'help':'Auto peak find control'})
        return config





class Module_SLD():   
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = slot
        self.prefix = f'CH{int(slot)}:'
        
        self.write(self.prefix+'NM')
        self.write(self.prefix+'MW')
        
    def write(self,command):
        self.dev.write(command)
        
    def read(self):
        return self.dev.read()
    
    def query(self,command):
        return self.dev.query(command)
    
    #--------------------------------------------------------------------------
    # Optional functions
    #--------------------------------------------------------------------------
        
    def setSafeState(self):
        self.setOutputState(False)
        if self.getOutputState() is False :
            return True
            
        
    def getID(self):
        return self.dev.query(self.prefix+'*IDN?')
        
        
    #--------------------------------------------------------------------------
    # Instrument variables
    #--------------------------------------------------------------------------

        
    def cleanResult(self,result):
        try:
            result=result.split(':')[1]
            result=result.split('=')[1]
            result=float(result)
        except:
            pass
        return result
    
    

        
    def getWavelength(self):
        result = self.query(self.prefix+'L?')
        result = self.cleanResult(result)
        return result
    
    
   
    
    
    def setPower(self,value):
        if value < 5:
            self.setOutputState(False)
        elif 5<=value<10 :
            if self.getOutputState() is False :
                self.setOutputState(True)
            self.write(self.prefix+'P=LOW')
            self.query('*OPC?')
        else :
            if self.getOutputState() is False :
                self.setOutputState(True)
            self.write(self.prefix+'P=HIGH')
            self.query('*OPC?')   
            
            
        
    def getPower(self):
        result = self.query(self.prefix+'P?')
        result = self.cleanResult(result)
        if result == 'Disabled':
            return 0
        elif result == 'HIGH':
            return 10
        elif result == 'LOW' :
            return 5
    
    
  
    
    
    def setOutputState(self,state):
        if state is True :
            self.write(self.prefix+"ENABLE")
        else :
            self.write(self.prefix+"DISABLE")
        self.query('*OPC?')
        
    def getOutputState(self):
        result = self.query(self.prefix+'ENABLE?')
        result = self.cleanResult(result)
        return result == 'ENABLED'
    



    def getDriverConfig(self):
        
        config = []
        config.append({'element':'variable','name':'power','type':float,'unit':'mW','read':self.getPower,'write':self.setPower,'help':'Output power'})
        config.append({'element':'variable','name':'output','type':bool,'read':self.getOutputState,'write':self.setOutputState,'help':'Output state'})
        return config
    
    
    
    
    
#ADDRESS = 'GPIB0::11::INSTR'
        
    
    
  
  
