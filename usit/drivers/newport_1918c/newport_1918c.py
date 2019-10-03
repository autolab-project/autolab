#!/usr/bin/env python3

"""
Supported instruments (identified): newport_1918c
- 
"""
import time
import ctypes as ct


class Driver():
    
    def __init__(self):
        self.write('PM:DS:Clear') # Clear data store
        self.write('PM:AUTO 1') # Automatic range
        self.write('PM:UNITs 2') # for Watts
    
    def getID(self):
        return self.query('*IDN?')
    
    
    def setZero(self):
        self.write('PM:ZEROSTOre')
        
        
        
    def setAutoRange(self,value):
        self.write(f'PM:AUTO {int(value)}')
        
    def getAutoRange(self):
        return bool(int(self.query('PM:AUTO?')))
        
        
        
        
    def setZeroValue(self,value):
        self.write(f'PM:ZEROVALue {float(value):.5f}')
        
    def getZeroValue(self):
        return float(self.query('PM:ZEROVALue?'))




    def setWavelength(self, wavelength):     
        self.write(f'PM:Lambda {int(wavelength)}')

    def getWavelength(self):
        return float(self.query('PM:Lambda?'))






    def setBufferSize(self,value):
        self.write(f'PM:DS:SIZE {int(value)}')
    
    def getBufferSize(self):
        return float(self.query('PM:DS:SIZE?'))
    
    
    
    

    def setBufferInterval(self,value): #ms
        self.write(f'PM:DS:INT {int(value)*10}') 
    
    def getBufferInterval(self):
        return float(self.query('PM:DS:INT?'))/10 
    
    
    def getPowerMean(self):

        """
        Stores the power values at a certain wavelength.
        """
        
        # On vide la mémoDL
        self.write('PM:DS:Clear')
        
        # On lance l'acquisition
        self.write('PM:DS:ENable 1')
        
        # On attend la fin de l'acquisition
        bufferSize = self.getBufferSize()
        bufferInterval = self.getBufferInterval()
        while int(self.query('PM:DS:Count?')) < bufferSize :
            time.sleep(bufferInterval)
        
        # On récupère les résultats de mesure
        mean=float(self.query('PM:STAT:MEAN?'))
        return mean        
    

    def getPower(self):
        while True :
            power = float(self.query('PM:Power?'))
            if power < 100 :
                break
            else :
                time.sleep(0.1)
        return power
        

    def getDriverConfig(self):
        
        config = []
        
        config.append({'element':'action','name':'zero','do':self.setZero,                       
                       'help':'Sets the zeroing value with the present reading.'})

        config.append({'element':'variable','name':'autorange','type':bool,
                       'read':self.getAutoRange,'write':self.setAutoRange,
                       'help':'Auto range enable command.'})

        config.append({'element':'variable','name':'zeroValue','type':float,
                       'read':self.getZeroValue,'write':self.setZeroValue,
                       'help':'Sets the zeroing value.'})

        config.append({'element':'variable','name':'bufferSize','type':int,
                       'read':self.getBufferSize,'write':self.setBufferSize,
                       'help':'Sets the size of the Data Store buffer.'})    

        config.append({'element':'variable','name':'bufferInterval','type':int,
                       'read':self.getBufferInterval,'write':self.setBufferInterval,
                       'help':'Set data store interval.'})   
    
        config.append({'element':'variable','name':'wavelength','type':float,
                       'read':self.getWavelength,'write':self.setWavelength,
                       'help':'Sets the wavelength for use when calculating power.'})      

        config.append({'element':'variable','name':'power','type':float,
                       'read':self.getPower,
                       'help':'Returns the power in the selected units.'})      
    
        config.append({'element':'variable','name':'powerMean','type':float,
                       'read':self.getPowerMean, 'help':'Mean power value at a certain wavelength.'})    
    
        return config


#################################################################################
############################## Connections classes ##############################
class Driver_DLL(Driver):
    
    def __init__(self,libpath=r'C:\Program Files\Newport\Newport USB Driver\Bin\usbdll.dll',**kwargs):
        
        self.productID=0xCEC7
        self.modelNumber=1918
        
        self.controller = ct.windll.LoadLibrary(libpath)
        
        # Open device
        cproductid = ct.c_int(self.productID)
        useusbaddress = ct.c_bool(1)
        num_devices = ct.c_int()
        status = self.controller.newp_usb_open_devices(cproductid, useusbaddress, ct.byref(num_devices))

        # Test ouverture
        if status != 0 or num_devices.value == 0:
            raise ValueError('Impossible to load the device')

        # Test device information
        arInstruments = ct.c_int()
        arInstrumentsModel = ct.c_int()
        arInstrumentsSN = ct.c_int()
        nArraySize = ct.c_int()
        status = self.controller.GetInstrumentList(ct.byref(arInstruments), 
                                                   ct.byref(arInstrumentsModel), 
                                                   ct.byref(arInstrumentsSN),
                                                   ct.byref(nArraySize))
        if status != 0 :
            raise ValueError('Impossible to load device information')

        # Test model number
        if arInstrumentsModel.value != self.modelNumber:
            raise ValueError('The device model number is not correct for this driver')
            
        self.IDnum = arInstruments.value
            
        Driver.__init__(self)
        
        
        
    def close(self):
        try: self.controller.newp_usb_uninit_system()
        except : pass

    def query(self,command):
        self.write(command)
        return self.read()


    def read(self):  
        try :         
            response = ct.create_string_buffer(1024)
            length = ct.c_ulong(1024)
            read_bytes = ct.c_ulong()
            cdevice_id = ct.c_long(self.IDnum)
            status = self.controller.newp_usb_get_ascii(cdevice_id, ct.byref(response), length, ct.byref(read_bytes))
            if status == 0:
                answer = response.value[0:read_bytes.value].decode().rstrip('\r\n')
                return answer
        except :
            pass

    def write(self, commandString):
        try :
            assert isinstance(commandString,str)
            query = ct.create_string_buffer(commandString.encode())
            length = ct.c_ulong(ct.sizeof(query))
            cdevice_id = ct.c_long(self.IDnum)
            self.controller.newp_usb_send_ascii(cdevice_id, ct.byref(query), length)
        except:
            pass
############################## Connections classes ##############################
#################################################################################
