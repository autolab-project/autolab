#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""

import time



class Device():
    
    def __init__(self):
    
        # Initialisation
        self.write('*CLS')      # Clear status registers
        self.write('DELAY 0')   # User commands not delayed
        
        # Subdevices
        self.tec = TEC(self)
        self.las = LAS(self)
        
        
    def getID(self):
        return self.query('*IDN?')
    
    
    def getDriverConfig(self):
        config = []
        config.append({'element':'module','name':'tec','object':self.tec})
        config.append({'element':'module','name':'las','object':self.las})
        return config
    
    
#################################################################################
############################## Connections classes ##############################
class Device_VISA(Device):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        import visa
        
        self.TIMEOUT = 15000 #ms
        
        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.get_instrument(address)
        self.controller.timeout = self.TIMEOUT
        self.controller.read_termination='\n'
        self.controller.write_termination='\n'
        self.controller.baud_rate = 19200
        #self.controller.query_delay = 0.05
        
        Device.__init__(self)

    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        result = self.controller.query(command)
        if '=' in result : result = result.split('=')[1]
        try : result = float(result)
        except: pass
        return result
    
    def write(self,command):
        self.controller.write(command)
        time.sleep(0.01)
        
class Device_GPIB(Device):
    def __init__(self,address=2,board_index=0,**kwargs):
        import Gpib
        
        self.inst = Gpib.Gpib(int(address),int(board_index))
        Device.__init__(self)
    
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


class LAS():
    
    def __init__(self,dev):
        
        self.dev = dev
        self.PRECISION = 0.1

    def write(self,command):
        self.dev.write(command)
        
    def query(self,command):
        return self.dev.query(command)
    
    
    def getCurrent(self):
        return float(self.query('LAS:LDI?'))

    def getCurrentSetpoint(self):
        return float(self.query('LAS:SET:LDI?'))
        
    def setCurrent(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'LAS:LDI {value}')
        self.query('*OPC?')
        if value > 0 :
            if self.isEnabled() is False :
                self.setEnabled(True)
            self.setMode('ILBW')
            self.waitForConvergence(self.getCurrent,value)
        elif value == 0 :
            if self.isEnabled() is True :
                self.setEnabled(False)




    def setPower(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'LAS:MDP {value}')
        self.query('*OPC?')
        if value > 0 :
            if self.isEnabled() is False :
                self.setEnabled(True)
            self.setMode('MDP')
            self.waitForConvergence(self.getPower,value)
        elif value == 0 :
            if self.isEnabled() is True :
                self.setEnabled(False)

    def getPower(self):
        self.query('*OPC?')
        return float(self.query('LAS:MDP?'))

    def getPowerSetpoint(self):
        return float(self.query('LAS:SET:MDP?'))
    
    
    
    
    def setEnabled(self,value):
        assert isinstance(value,bool)
        self.write(f'LAS:OUT {int(value)}')
        self.query('*OPC?')
        if value is True :
            mode = self.query('LAS:MODE?')
            if mode.startswith('I'):
                self.waitForConvergence(self.getCurrent,
                                        self.getCurrentSetpoint())
            elif mode.startswith('MD'):
                self.waitForConvergence(self.getPower,
                                        self.getPowerSetpoint())
        
    def isEnabled(self):
        return bool(int(self.query('LAS:OUT?')))

    
    
    
    def waitForConvergence(self,func,setPoint):
        tini = time.time()
        while True :
            try : 
                if abs(func()-setPoint) < self.PRECISION*setPoint :
                    break
                else :
                    time.sleep(0.5)
            except :
                pass
            if time.time() - tini > 5 :
                break
            
            
            
            
    def setMode(self,mode):
        assert isinstance(mode,str)
        currMode = self.getMode()
        enabledMode = self.isEnabled()
        if currMode != mode :
            self.write(f'LAS:MODE:{mode}')
            self.query('*OPC?')
            self.setEnabled(enabledMode)
            
    def getMode(self):
        return self.query('LAS:MODE?')
        
        
    
    
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'currentSetpoint','type':float,'unit':'mA','read':self.getCurrentSetpoint,'write':self.setCurrentSetpoint,'help':'Current setpoint'})
        config.append({'element':'variable','name':'current','type':float,'unit':'mA','read':self.getCurrent,'help':'Current'})
        config.append({'element':'variable','name':'powerSetpoint','type':float,'unit':'mW','read':self.getPowerSetpoint,'write':self.setPowerSetpoint,'help':'Output power setpoint'})
        config.append({'element':'variable','name':'power','type':float,'unit':'mW','read':self.getPower,'help':'Output power'})
        config.append({'element':'variable','name':'output','type':bool,'read':self.isEnabled,'write':self.setEnabled,'help':'Output state'})
        config.append({'element':'variable','name':'mode','type':str,'read':self.getMode,'write':self.setMode,'help':'Control mode'})
        return config
    
    



class TEC():
    
    def __init__(self,dev):
        
        self.dev = dev
        self.PRECISION = 0.05



    def write(self,command):
        self.dev.write(command)
        
    def query(self,command):
        return self.dev.query(command)
    
    
    

    def getResistance(self):
        return float(self.query('TEC:R?'))



    def setGain(self,value):
        assert isinstance(int(value),int)
        value = int(value)
        self.write(f'TEC:GAIN {value}')
        self.query('*OPC?')
        
    def getGain(self):
        return int(float(self.query('TEC:GAIN?')))
   
    

    
    def getCurrent(self):
        return float(self.query('TEC:ITE?'))

    def getCurrentSetpoint(self):
        return float(self.query('TEC:SET:ITE?'))
        
    def setCurrent(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'TEC:ITE {value}')
        self.query('*OPC?')
        if value > 0 :
            if self.isEnabled() is False :
                self.setEnabled(True)
            self.setMode('ITE')
            self.waitForConvergence(self.getCurrent,value)
        elif value == 0 :
            if self.isEnabled() is True :
                self.setEnabled(False)




    def setTemperature(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'TEC:T {value}')
        self.query('*OPC?')
        if value > 0 :
            if self.isEnabled() is False :
                self.setEnabled(True)
            self.setMode('T')
            self.waitForConvergence(self.getTemperature,value)
        elif value == 0 :
            if self.isEnabled() is True :
                self.setEnabled(False)

    def getTemperature(self):
        return float(self.query('TEC:T?'))

    def getTemperatureSetpoint(self):
        return float(self.query('TEC:SET:T?'))
    
    

    
    
    def setEnabled(self,value):
        assert isinstance(value,bool)
        self.write(f'TEC:OUT {int(value)}')
        self.query('*OPC?')
        if value is True :
            mode = self.query('TEC:MODE?')
            if mode.startswith('I'):
                self.waitForConvergence(self.getCurrent,
                                        self.getCurrentSetpoint())
            elif mode.startswith('T'):
                self.waitForConvergence(self.getTemperature,
                                        self.getTemperatureSetpoint())
        
    def isEnabled(self):
        return bool(int(self.query('TEC:OUT?')))
    
    
    
    
    
    def waitForConvergence(self,func,setPoint):
        tini = time.time()
        while True :
            try : 
                if abs(func()-setPoint) < self.PRECISION*setPoint :
                    break
                else :
                    time.sleep(0.5)
            except :
                pass
            if time.time() - tini > 5 :
                break
            
            
            
            
    def setMode(self,mode):
        assert isinstance(mode,str)
        currMode = self.getMode()
        enabledMode = self.isEnabled()
        if currMode != mode :
            self.write(f'TEC:MODE:{mode}')
            self.query('*OPC?')
            self.setEnabled(enabledMode)
            
    def getMode(self):
        return self.query('TEC:MODE?')
    
    
    
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'resistance','type':float,'read':self.getResistance,'help':'Resistance'})
        config.append({'element':'variable','name':'gain','type':int,'read':self.getGain,'write':self.setGain,'help':'Gain'})
        config.append({'element':'variable','name':'currentSetpoint','type':float,'unit':'mA','read':self.getCurrentSetpoint,'write':self.setCurrentSetpoint,'help':'Current setpoint'})
        config.append({'element':'variable','name':'current','type':float,'unit':'mA','read':self.getCurrent,'help':'Current'})
        config.append({'element':'variable','name':'temperatureSetpoint','type':float,'unit':'°C','read':self.getTemperatureSetpoint,'write':self.setTemperatureSetpoint,'help':'Temperature setpoint'})
        config.append({'element':'variable','name':'temperature','type':float,'unit':'°C','read':self.getTemperature,'help':'Actual temperature'})
        config.append({'element':'variable','name':'output','type':bool,'read':self.isEnabled,'write':self.setEnabled,'help':'Output state'})
        config.append({'element':'variable','name':'mode','type':str,'read':self.getMode,'write':self.setMode,'help':'Control mode'})
        return config
    
    
        
        
        
if __name__ == '__main__':
    
    from optparse import OptionParser
    import inspect
    import sys

    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_ilxlightwaveldc3724 -i 2 -b 0 -a 30 -t 20.1
                   set the pump current to 30 mA and the temperature to 20.1 degree celcius. The gpib address is set to 19 and the board number to 0.
               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="command", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="query", default=None, help="Set the query to use." )
    parser.add_option("-a", "--current", type="str", dest="current", default=None, help="Set the pump current in mA." )
    parser.add_option("-p", "--power", type="str", dest="power", default=None, help="Set the pump power in ?." )
    parser.add_option("-t", "--temperature", type="str", dest="temperature", default=None, help="Set the locking temperature." )
    parser.add_option("-i", "--address", type="str", dest="address", default='GPIB0::2::INSTR', help="Set the GPIB address to use to communicate." )
    parser.add_option("-b", "--board_index", type='str', dest="board_index", default='0', help="Set the GPIB address to use to communicate." )
    parser.add_option("-l", "--link", type="string", dest="link", default='GPIB', help="Set the connection type." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    classes = [name for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass) if obj.__module__ is __name__]
    assert 'Device_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Device_')])
    Device_LINK = getattr(sys.modules[__name__],'Device_'+options.link)
    I = Device_LINK(address=options.address,board_index=options.board_index)
    
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
    
    if options.current:
        I.las.setCurrent(options.current)
    if options.power:
        # to sort out what power does and the unit
        #I.las.setPower(options.power)
        pass
    if options.temperature:
        if (eval(options.temperature) > 18) and (eval(options.temperature) < 25):
            I.tec.setTemperature(options.temperature)
    
    sys.exit()

        
