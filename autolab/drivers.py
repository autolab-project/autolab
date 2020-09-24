# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 14:57:12 2020

@author: qchat
"""

from .core.utilities import print_tab
from .core import drivers
import git

class DriverManager() :
    def __init__(self) :
        # Load list of drivers
        self.DEMO_updated = False
    
    def summary(self) :
        pass
        # Print list of drivers sorted by name and category with their last version
        # Content to be dynamical of course
        #drivers_list = drivers.load_paths()
        #print(drivers_list)
        # tab_content = [['Driver category','Driver name','Last version'],None]
        # if self.DEMO_updated is False :
        #     tab_content.append(['Light source','yenista_TUNICS','1.0.0'])
        #     tab_content.append(['','yenista_OSICS','1.1.2'])
        #     tab_content.append(None)
        #     tab_content.append(['Power meter','exfo_LTB1','1.0.0'])
        #     tab_content.append(['','exfo_PM1613','2.1.0'])
        #     tab_content.append(['','thorlabs_ITC4001','1.0.0'])
        # else :
        #     tab_content.append(['Light source','yenista_TUNICS','1.0.0'])
        #     tab_content.append(['','yenista_OSICS','1.1.2'])
        #     tab_content.append(None)
        #     tab_content.append(['Power meter','exfo_LTB1','1.2.1'])
        #     tab_content.append(['','exfo_PM1613','2.5.0'])
        #     tab_content.append(['','thorlabs_ITC4001','2.0.1'])
        #     tab_content.append(None)
        #     tab_content.append(['Oscilloscope','tektronix_DPO4104','1.0.1'])
        #     tab_content.append(['','lecroy_WAVEMASTER','1.0.0'])
        # tab_content.append(None)
        # print_tab(tab_content)
        
        
    def update(self):
        
        from .core import repo
        repo.sync()       
        
        # # Update drivers codes from github repo autolab-drivers
        # if self.DEMO_updated is False :
        #     self.DEMO_updated = True
        #     print('Updated 3 existing drivers. Added 2 new drivers')
        # else :
        #     print('Already up-do-date')

    def releases_notes(self,driver_name) :
        # Print releases note of a particular driver
        print(f" Driver {driver_name}")
        print('')
        tab_content = [['Version (date)','Releases notes'],None]
        tab_content.append(['1.0.0 (01/01/2020)','First release'])
        tab_content.append(['','Added function set_amplitude'])
        tab_content.append(None)
        tab_content.append(['1.1.0 (04/02/2020)','Fixed bug in function set_amplitude'])
        tab_content.append(['','Added function set_wavelength'])
        tab_content.append(None)
        tab_content.append(['1.2.1 (08/03/2020)','Fixed bug in function set_wavelength'])
        tab_content.append(None)        
        print_tab(tab_content)

    def configuration_example(self,driver_name):

        if driver_name == 'exfo_LTB1' :
            print('[my_exfo_LTB1]')
            print('driver = exfo_LTB1')
            print('connection = TELNET')
            print('address = 192.168.0.9')
            print('slot1 = FTB1750')
            print('slot1_name = channel1')
            print('slot2 = FTB1750')
            print('slot2_name = channel2')

def get_driver_instance(connection_params) :
    if connection_params['driver'] == 'yenista_TUNICS' : return Driver_tunics()
    elif connection_params['driver'] == 'autolab_SERVER' : return Driver_server()

class Driver_tunics :
    def __init__(self):
        self.wl = 1550
        self.pwr = 0
    
    def set_wavelength(self,value):
        self.wl = value
    def get_wavelength(self):
        return self.wl

    def set_power(self,value):
        self.pwr = value
    def get_power(self):
        return self.pwr

    def get_device_structure(self):
        structure = []
        structure.append({'type':'Variable','name':'wavelength','set_method':self.set_wavelength,'get_method':self.get_wavelength,'unit':'nm','description':'Wavelength of the output light'})
        structure.append({'type':'Variable','name':'power','set_method':self.set_power,'get_method':self.get_power,'unit':'mW', 'description':'Power of the output light'})
        return structure


class Driver_server :
    def __init__(self):
        self.wl = 1550
        self.pwr = 0
    
    def set_wavelength(self,value):
        self.wl = value
    def get_wavelength(self):
        return self.wl

    def set_power(self,value):
        self.pwr = value
    def get_power(self):
        return self.pwr

    def get_device_structure(self):
        structure = []
        structure.append({'type':'Device', 'name':'my_spectrometer', 'connector':lambda : self.connect_remote_device('my_spectrometer')})
        return structure

    def connect_remote_device(self,device_name) :
        instance = RemoteDeviceWrapper(self,device_name)
        structure = []
        structure.append({'type':'Variable','name':'temperature','set_method':lambda x: instance.set_variable('temperature',x),'get_method':lambda : instance.get_variable('temperature'),'unit':'°C','description':'Temperature of the detector'})
        structure.append({'type':'Variable','name':'spectrum','get_method':lambda : instance.get_variable('spectrum'),'description':'Current spectrum'})
        structure.append({'type':'Variable','name':'exposure_time','set_method':lambda x : instance.set_variable('exposure_time',x),'get_method':lambda : instance.get_variable('exposure_time'),'unit':'s','description':'Exposure time of the detector'})
        return instance,structure

class RemoteDeviceWrapper :
    def __init__(self,server_driver,device_name):
        self.server_driver = server_driver
    def get_variable(self,variable_name):
        if variable_name == 'temperature' :
            return -90
    def set_variable(self,variable_name,value=None):
        pass

