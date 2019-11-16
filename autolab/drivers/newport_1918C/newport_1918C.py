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
    
    def get_id(self):
        return self.query('*IDN?')
    
    
    def zero(self):
        self.write('PM:ZEROSTOre')
        
        
        
    def set_auto_range(self,value):
        self.write(f'PM:AUTO {int(value)}')
        
    def get_auto_range(self):
        return bool(int(self.query('PM:AUTO?')))
        
        
        
        
    def set_zero_value(self,value):
        self.write(f'PM:ZEROVALue {float(value):.5f}')
        
    def get_zero_value(self):
        return float(self.query('PM:ZEROVALue?'))




    def set_wavelength(self, wavelength):     
        self.write(f'PM:Lambda {int(wavelength)}')

    def get_wavelength(self):
        return float(self.query('PM:Lambda?'))






    def set_buffer_size(self,value):
        self.write(f'PM:DS:SIZE {int(value)}')
    
    def get_buffer_size(self):
        return float(self.query('PM:DS:SIZE?'))
    
    
    
    

    def set_buffer_interval(self,value): #ms
        self.write(f'PM:DS:INT {int(value)*10}') 
    
    def get_buffer_interval(self):
        return float(self.query('PM:DS:INT?'))/10 
    
    
    def get_power_mean(self):

        """
        Stores the power values at a certain wavelength.
        """
        
        # On vide la mémoDL
        self.write('PM:DS:Clear')
        
        # On lance l'acquisition
        self.write('PM:DS:ENable 1')
        
        # On attend la fin de l'acquisition
        buffer_size = self.get_buffer_size()
        buffer_interval = self.get_buffer_interval()
        while int(self.query('PM:DS:Count?')) < buffer_size :
            time.sleep(buffer_interval)
        
        # On récupère les résultats de mesure
        mean=float(self.query('PM:STAT:MEAN?'))
        return mean        
    

    def get_power(self):
        while True :
            power = float(self.query('PM:Power?'))
            if power < 100 :
                break
            else :
                time.sleep(0.1)
        return power
        

    def get_driver_model(self):
        
        model = []
        
        model.append({'element':'action','name':'zero','do':self.zero,                       
                       'help':'Sets the zeroing value with the present reading.'})

        model.append({'element':'variable','name':'autorange','type':bool,
                       'read':self.get_auto_range,'write':self.set_auto_range,
                       'help':'Auto range enable command.'})

        model.append({'element':'variable','name':'zero_value','type':float,
                       'read':self.get_zero_value,'write':self.set_zero_value,
                       'help':'Sets the zeroing value.'})

        model.append({'element':'variable','name':'buffer_size','type':int,
                       'read':self.get_buffer_size,'write':self.set_buffer_size,
                       'help':'Sets the size of the Data Store buffer.'})    

        model.append({'element':'variable','name':'buffer_interval','type':int,
                       'read':self.get_buffer_interval,'write':self.set_buffer_interval,
                       'help':'Set data store interval.'})   
    
        model.append({'element':'variable','name':'wavelength','type':float,
                       'read':self.get_wavelength,'write':self.set_wavelength,
                       'help':'Sets the wavelength for use when calculating power.'})      

        model.append({'element':'variable','name':'power','type':float,
                       'read':self.get_power,
                       'help':'Returns the power in the selected units.'})      
    
        model.append({'element':'variable','name':'power_mean','type':float,
                       'read':self.get_power_mean, 'help':'Mean power value at a certain wavelength.'})    
    
        return model


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
