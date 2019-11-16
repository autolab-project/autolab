#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

from XPS import XPS


class Driver():

    slot_config = '<MODULE_NAME>,<NAME_IN_XPS>,<CALIBRATION_PATH>'

    def __init__(self,**kwargs):
        
        # Submodules loading
        self.slot_names = {}
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix) and not '_name' in key :
                slot_num = key[len(prefix):]
                module_name, name_in_xps, calib_path = [a.strip() for a in kwargs[key].split(',')]
                module_class = globals()[f'Module_{module_name}']
                if f'{key}_name' in kwargs.keys() : name = kwargs[f'{key}_name']
                else : name = f'{key}_{module_name}'
                setattr(self,name,module_class(self,name_in_xps,calib_path))
                self.slot_names[slot_num] = name

        
    def get_driver_model(self):
        model = [{'element':'module','name':name,'object':getattr(self,name)}
                 for name in self.slot_names.values() ]
        return model

    
    
#################################################################################
############################## Connections classes ##############################
class Driver_SOCKET(Driver):
    
    def __init__(self,address='192.168.0.8',**kwargs):
    
        self.TIMEOUT = 2
        
        # Instantiation
        self.controller = XPS()
        self.socketID = self.controller.TCP_ConnectToServer(address,5001,self.TIMEOUT)

        Driver.__init__(self,**kwargs)


    def isConnected(self):
        try :
            assert self.controller.FirmwareVersionGet(self.socketID) is not None
            return True
        except :
            return False
        
        
    def query(self,command,**kwargs):
        
        assert isinstance(command,list)
        assert hasattr(self.controller,command[0])

        if len(command)>1 :
            ans = getattr(self.controller,command[0])(self.socketID,*command[1:])
        else :
            ans = getattr(self.controller,command[0])(self.socketID)
            
        if ans[1] != '' :
            if len(ans)>2:
                return ans[1:]
            else :
                return ans[1]
        
    def close(self):
        try : self.controller.TCP_CloseSocket(self.socketId)
        except : pass
         
############################## Connections classes ##############################
#################################################################################
    
import time
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d

class Module_NSR1():
    
    category = 'Rotation stage'
    
    def __init__(self,dev,slot,calibration_path):
        
        self.dev = dev
        self.NAME = slot
        self.SLOT = slot
        
        self.calibration_path = calibration_path
        assert os.path.exists(calibration_path)
        self.calibration_function = None
        
        self.calib = None
        self.load_calibration()
        
    #--------------------------------------------------------------------------
    # Calibration functions
    #--------------------------------------------------------------------------
    
    def load_calibration(self):
        try: self.calib = pd.read_csv(os.path.join(self.calibration_path,'calib.csv'))
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
        filepath=os.path.join(self.calibration_path,f'{date}_{self.NAME}_calib.jpg')
        fig.savefig(filepath,bbox_inches='tight',dpi=300)
        fig.close()
           
        # Enregistrement des données 
        df.to_csv(os.path.join(self.calibration_path,'calib.csv'))
        
        # Raffraichissement des donnees
        self.load_calibration()
        

        
        
        
        
    #--------------------------------------------------------------------------
    # Optional functions
    #--------------------------------------------------------------------------
        
    def safe_state(self):
        self.set_min()
        if self.get_transmission() < 0.2 :
            return True
            

        

        
    #--------------------------------------------------------------------------
    # Technical functions
    #--------------------------------------------------------------------------
    
    def get_filter_state(self):
        state=self.dev.query(['GroupStatusGet',self.SLOT])
        
        if 0 <= state <= 9 :
            return 'NOTINIT'
        elif state == 42 :
            return 'NOTREF'
        elif state == 43 :
            return 'HOMING'
        elif state == 44 :
            return 'MOVING'
        elif 10 <= state <= 19 :
            return 'ENABLED'
        elif 20 <= state <= 39 :
            return 'DISABLED'
        else :
            return None
    
    def check_ready_state(self):
    
        if self.get_filter_state() in ['ENABLED','DISABLED'] :
            return True 
        else :
            if self.get_filter_state() == 'NOTINIT' :
                self.dev.query(['GroupInitialize',self.SLOT])
                if self.get_filter_state() != 'NOTREF' :
                    return False
            if self.get_filter_state() == 'NOTREF':
                self.dev.query(['GroupHomeSearch',self.SLOT])
                while self.get_filter_state() == 'HOMING' :
                    time.sleep(0.5)
                if self.get_filter_state() in ['ENABLED','DISABLED'] :
                    self.set_enabled(False)
                    return True
                else :
                    return False
                
    
    def wait_move_ending(self):
        while self.get_filter_state() == 'MOVING' :
            time.sleep(0.1)
        time.sleep(0.4) # Trop rapide sinon
        
        
        
        
        
        
    def set_enabled(self,state):
        assert isinstance(state,bool)
        if state is True :
            self.dev.query(['GroupMotionEnable',self.SLOT])
        else :
            self.dev.query(['GroupMotionDisable',self.SLOT])       

    def is_enabled(self):
        state=self.get_filter_state()
        if state in ['ENABLED','MOVING'] :
            return True
        else :
            return False
        
        
        
        

    def set_positioner_name(self,value):
        assert isinstance(value,str)
        self.set_data('positionerName',value)
        
    def get_positioner_name(self):
        if 'positionerName' not in self.get_dataList() :
            self.set_positioner_name('Pos')
        return self.get_data('positionerName')
    
    
    
        
    #--------------------------------------------------------------------------
    # Instrument variables
    #--------------------------------------------------------------------------
    
    
    
    def get_parameters(self):
        if self.check_ready_state() is True :
            params={}
            temp=self.dev.query(['PositionerSGammaParametersGet',self.SLOT+'.'+self.get_positioner_name()])       
            params['velocity']=temp[0]
            params['acceleration']=temp[1]
            params['minJerkTime']=temp[2]
            params['maxJerkTime']=temp[3]
            return params
        else :
            raise ValueError('Not ready')
            
    def set_parameters(self,params):
        if self.check_ready_state() is True :
            self.dev.query(['PositionerSGammaParametersSet',self.SLOT+'.'+self.get_positioner_name(),
                                                             params['velocity'],
                                                             params['acceleration'],
                                                             params['minJerkTime'],
                                                             params['maxJerkTime']]) 
        else :
            raise ValueError('Not ready')






    def set_velocity(self,value):
        assert isinstance(float(value),float)
        value=float(value)
        params=self.get_parameters()
        params['velocity']=value
        self.set_parameters(params)
    
    def get_velocity(self):
        return float(self.get_parameters()['velocity'])


        
    


    def set_acceleration(self,value):
        assert isinstance(float(value),float)
        value=float(value)
        params=self.get_parameters()
        params['acceleration']=value
        self.set_parameters(params)
    
    def get_acceleration(self):
        return float(self.get_parameters()['acceleration'])
    



    
    
    def set_angle(self,value,forced=False):
        assert isinstance(float(value),float)
        value=float(value)
        
        if forced is False :
            curr_angle = self.get_angle()
            if value > curr_angle - 1.9 :
                self.set_angle(value+20,forced=True)
            
        if self.check_ready_state() is True :
            self.set_enabled(True)
            self.dev.query(['GroupMoveAbsolute',self.SLOT,[value]])
            self.wait_move_ending()
            self.set_enabled(False)
        else :
            raise ValueError('Not ready')
        
    def get_angle(self):
        if self.check_ready_state() is True :
            value = float(self.dev.query(['GroupPositionCurrentGet',self.SLOT,1]))
            return value
        else :
            raise ValueError('Not ready')
    
    
    
    
    

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





        



    
      
    
    def set_min(self):
        self.set_transmission(0)
        
    def set_max(self):
        self.set_transmission(1)



            
    
    def go_home(self):
        
        self.set_angle(self.get_angle()+5) # In case we are at home - blocking
        
        # Go to not init
        self.dev.query(['GroupKill',self.SLOT])
        while self.get_filter_state() != 'NOTINIT':
            time.sleep(0.1)
                            
        # Go from not init to ref mode
        self.dev.query(['GroupInitialize',self.SLOT])
        while self.get_filter_state() != 'NOTREF':
            time.sleep(0.1)
        
        # Homing to get back to ready state
        self.dev.query(['GroupHomeSearch',self.SLOT])
        while self.get_filter_state() != 'ENABLED':
            time.sleep(0.1)

        # On le désactive
        self.set_enabled(False)
        while self.get_filter_state() != 'DISABLED':
            time.sleep(0.1)
            
            
            
            
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
    

