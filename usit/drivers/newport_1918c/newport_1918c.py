# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 21:17:28 2019

@author: quentin.chateiller
"""
import time
import ctypes as ct

LIBPATH = r'C:\Program Files\Newport\Newport USB Driver\Bin\usbdll.dll'

class Device():
    
    def __init__(self,libpath=LIBPATH):
        
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
            
        self.write('PM:DS:Clear') # Clear data store
        self.write('PM:AUTO 1') # Automatic range
        self.write('PM:UNITs 2') # for Watts
        
        
        
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
        
    #--------------------------------------------------------------------------
    # Optional functions
    #--------------------------------------------------------------------------
    
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
        :param wavelength: float: Wavelength at which this operation should be done. float.
        :param buff_size: int: nuber of readings that will be taken
        :param interval_ms: float: Time between readings in ms.
        :return: [actualwavelength,mean_power,std_power]
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
        
a=Device()