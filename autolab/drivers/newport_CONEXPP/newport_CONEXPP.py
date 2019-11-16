#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


import time 
import os
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d

import numpy as np
import pandas as pd

class Driver():
    
    slot_config = '<MODULE_NAME>,<CALIBRATION_PATH>'
    
    def __init__(self,**kwargs):
        
        # Submodules loading
        self.slot_names = {}
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix) and not '_name' in key :
                slot_num = key[len(prefix):]
                module_name, calib_path = [a.strip() for a in kwargs[key].split(',')]
                module_class = globals()[f'Module_{module_name}']
                if f'{key}_name' in kwargs.keys() : name = kwargs[f'{key}_name']
                else : name = f'{key}_{module_name}'
                setattr(self,name,module_class(self,slot_num,name,calib_path))
                self.slot_names[slot_num] = name
        
        
    def get_driver_model(self):
        
        model = []
        for name in self.slot_names.values() :
            model.append({'element':'module','name':name,'object':getattr(self,name)})
        return model
        
        
    
#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        import visa
        
        
        self.BAUDRATE = 115200
        
        # Initialisation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.baud_rate = self.BAUDRATE
        
        Driver.__init__(self,**kwargs)
        
        
        
    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\r\n')
        return result
    
    def write(self,command):
        self.controller.write(command)
        
        
############################## Connections classes ##############################
#################################################################################

class Module_NSR1():
    
    def __init__(self,dev,slot,name,calibPath):
        
        self.dev = dev
        self.NAME = name
        self.SLOT = slot
        
        self.check_notref_state()
    
        self.calibPath = calibPath
        assert os.path.exists(calibPath)
        self.calibration_function = None
        
        self.calib = None
        self.load_calibration()
        
        
        
    # Query write functions
    # =========================================================================  

    def query(self,command,unwrap=True) :
        result = self.dev.query(self.SLOT+command)
        if unwrap is True :
            try:
                prefix=self.SLOT+command[0:2]
                result = result.replace(prefix,'')
                result = result.strip()
                result = float(result)
            except:
                pass
        return result
        
    def write(self,command) :
        self.dev.write(self.SLOT+command)
    
       
    # Drivers functions
    # =========================================================================
            
    def get_id(self):
        return self.query('ID?')
    
    
    
    def get_filter_state(self):
        ans = self.query('TS?',unwrap=False)[-2:]
        if ans[0] == '0' :
            return 'REF'
        elif ans == '14' :
            return 'CONF'
        elif ans == '1E' :
            return 'HOMING'
        elif ans == '28' :
            return 'MOVING'
        elif ans[0] == '3' and ( ans[1].isalpha() is False)  :
            return 'ENABLED'
        elif ans[0] == '3' and ( ans[1].isalpha() is True)  :
            return 'DISABLED'
        else :
            return 'UNKNOWN'


        
    def check_notref_state(self):
        
        # On vérifie que l'on est pas dans le mode REF
        state=self.get_filter_state()
        if state == 'REF' :
            self.write('OR') # Perfom Home search
            while self.get_filter_state() == 'HOMING' :
                time.sleep(0.5)
        elif state == 'CONF' :    
            self.write('PW0') # Sortie du mode Configuration
            self.check_notref_state()
            
    def wait_move_ending(self):
        while self.get_filter_state() == 'MOVING' :
            time.sleep(0.1)

    
    
    
    def set_enabled(self,value):
        assert isinstance(bool(value),bool)
        self.write('MM'+str(int(value)))
    
    def is_enabled(self):
        state=self.get_filter_state()
        if state in ['ENABLED','MOVING'] :
            return True
        else :
            return False
        
        

        
        
    #--------------------------------------------------------------------------
    # Instrument variables
    #--------------------------------------------------------------------------
    
    
 
    
    def set_velocity(self,value):
        
        assert isinstance(int(value),int)
        value=int(value)
        
        if value != self.get_velocity():
            
            # Go to not ref mode
            self.write('RS')
            while self.get_filter_state() != 'REF':
                time.sleep(0.1)
            
            # Go to config mode
            self.write('PW1')
            while self.get_filter_state() != 'CONF':
                time.sleep(0.1)
            
            # Change value
            self.write('VA%i'%value)

            # Sortie du mode config
            self.write('PW0')
            while self.get_filter_state() != 'REF':
                time.sleep(0.1)
            
            # Homing to get back to ready state
            self.write('OR')
            while self.get_filter_state() != 'ENABLED':
                time.sleep(0.1)

            # On le désactive
            self.set_enabled(False)
            while self.get_filter_state() != 'DISABLED':
                time.sleep(0.1)
    
    def get_velocity(self):
        return self.query('VA?')
    
    
    def set_acceleration(self,value):
        
        assert isinstance(int(value),int)
        value=int(value)
        
        if value != self.get_velocity():
            
            # Go to not ref mode
            self.write('RS')
            while self.get_filter_state() != 'REF':
                time.sleep(0.1)
            
            # Go to config mode
            self.write('PW1')
            while self.get_filter_state() != 'CONF':
                time.sleep(0.1)
            
            # Change value
            self.write('AC%i'%value)

            # Sortie du mode config
            self.write('PW0')
            while self.get_filter_state() != 'REF':
                time.sleep(0.1)
            
            # Homing to get back to ready state
            self.write('OR')
            while self.get_filter_state() != 'ENABLED':
                time.sleep(0.1)

            # On le désactive
            self.set_enabled(False)
            while self.get_filter_state() != 'DISABLED':
                time.sleep(0.1)
    
        
    def get_acceleration(self):
        return self.query('AC?')
    
            
            
    
    
    
    def set_angle(self,value,forced=False):
        assert isinstance(float(value),float)
        value=float(value)
        
        if forced is False :
            curr_angle = self.get_angle()
            if value > curr_angle - 1.9 :
                self.set_angle(value+20,forced=True)
            
        self.set_enabled(True)
        self.write('PA'+str(value))
        self.wait_move_ending()
        self.set_enabled(False)
        
    def get_angle(self):
        value = self.query('TP?')
        return value
       
    
    
    
    
    
    def set_min(self):
        self.set_transmission(0)
        
    def set_max(self):
        self.set_transmission(1)





    def set_transmission(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        angle = self.get_angle_from_transmission(value)
        self.set_angle(angle)
    
    def get_transmission(self):
        angle = self.get_angle()
        return self.get_transmission_from_angle(angle) 

    def get_transmission_max(self):
        return self.calib.transmission.max()



    def get_angle_from_transmission(self,value):
        ind = abs(self.calib.transmission-value).idxmin()
        return float(self.calib.loc[ind,'angle'])   
    
    def get_transmission_from_angle(self,value):
        ind = abs(self.calib.angle-value).idxmin()
        return float(self.calib.loc[ind,'transmission'])   


    
    def go_home(self):
                            
        # Go to not ref mode
        self.write('RS')
        while self.get_filter_state() != 'REF':
            time.sleep(0.1)
        
        # Homing to get back to ready state
        self.write('OR')
        while self.get_filter_state() != 'ENABLED':
            time.sleep(0.1)

        # On le désactive
        self.set_enabled(False)
        while self.get_filter_state() != 'DISABLED':
            time.sleep(0.1)
            
            
            
    # Calibration functions
    # =========================================================================
    
    def load_calibration(self):
        try: self.calib = pd.read_csv(os.path.join(self.calibPath,'calib.csv'))
        except: pass
    
    def set_calibration_function(self,calibration_function):
        self.calibration_function = calibration_function
        
    def calibrate(self):
        
        assert self.calibration_function is not None
        
        def scan(list_angle):
            
            df = pd.DataFrame()

            for angle_setpoint in list_angle :
                self.set_angle(angle_setpoint)
                angle=self.get_angle()
                power=self.calibration_function()
                df=df.append({'angle':angle,'power':power})
                   
            df.sort_values(by=['angle'],inplace=True)
            return df
        
        plt.ioff()
        fig = plt.figure()
        ax=fig.add_subplot(111)
        
        # Homing
        self.go_home()
        
        # Fabrication de la liste des angles à explorer
        list_angle = np.concatenate((np.arange(0,360,8),np.arange(4,360,8)))
        list_angle = np.flipud(list_angle)
        
        # Lancement du scan de mesure de puissance
        df=scan(list_angle)
        
        # Find transition
        derivative = np.diff(df.power)
        imax=np.argmax(derivative)
        
        # Recoupage
        df_shifted = pd.DataFrame()
        df_shifted['power'] = np.concatenate((df.power[imax:],df.power[0:imax]))
        df_shifted['angle'] = np.concatenate((df.angle[imax:]-360,df.angle[0:imax]))
        df = df_shifted
        
        # Suppression transition sur 10deg
        df = pd.DataFrame()
        df = df[df.angle>(df.angle.min()+10)]
        df = df[df.angle<(df.angle.max()-10)]
        
        # Normalisation
        df['transmission']=df.power/df.power.max()
        ax.plot(df.angle,df.transmission,'x',label='raw')
        
        # Lissage
        df['transmission']=savgol_filter(df.transmission, 7, 3)
        
        # Interpolation
        interpolFunc=interp1d(df.angle, df.transmission, kind='cubic')
        df['angle']=np.linspace(df.angle.min(),df.angle.max(),1000)
        df['transmission']=interpolFunc(df.angle)
        
        # EXTRACT On ne garde que entre 0% et 95% car trop bruité au dessus
        df = df[df.transmission<0.95]
        
        # Sauvegarde plot
        date=time.strftime("%Y%m%d_%H%M%S")
        ax.plot(df.angle,df.transmission,'r-',label='Final')
        ax.set_title(f'{self.NAME} filter {date}')
        ax.grid()
        ax.set_xlabel('Angle [deg]')
        ax.set_ylabel('Power [a.u.]')
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc=0)
        filepath=os.path.join(self.calibPath,f'{date}_{self.NAME}_calib.jpg')
        fig.savefig(filepath,bbox_inches='tight',dpi=300)
        fig.close()
           
        # Enregistrement des données 
        df.to_csv(os.path.join(self.calibPath,'calib.csv'))
        
        # Raffraichissement des donnees
        self.load_calibration()
     
        
    def get_driver_model(self):
        
        model = []
        model.append({'element':'variable','name':'velocity','type':float,'read':self.get_velocity,'write':self.set_velocity,'help':'Velocity of the filter during move'})
        model.append({'element':'variable','name':'acceleration','type':float,'read':self.get_acceleration,'write':self.set_acceleration,'help':'Acceleration of the filter during move'})
        model.append({'element':'variable','name':'angle','type':float,'read':self.get_angle,'write':self.set_angle,'help':'Current angle position'})
        model.append({'element':'variable','name':'transmission','type':float,'read':self.get_transmission,'write':self.set_transmission,'help':'Current transmission of the filter'})
        model.append({'element':'action','name':'set_min','do':self.set_min,'help':'Go to minimum transmission'})
        model.append({'element':'action','name':'set_max','do':self.set_max,'help':'Go to maximum transmission'})
        model.append({'element':'action','name':'go_home','do':self.go_home,'help':'Go to home position'})
        return model
    
    
        
        
    
