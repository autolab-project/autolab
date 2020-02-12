#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import os
import time
from numpy import savetxt,ndarray


class Driver():
    
    def __init__(self,camera='Camera1'):
        self.camera = camera
        
    def set_camera(self,camera):
        self.write(f'CONNECT={camera}')
        self.camera = camera
    def set_nb_frames(self,nb_frames):
        self.write(f'NBFRAMES={nb_frames}')
    def set_exposure(self,exposure):
        self.write(f'EXPTIME={exposure}')
        
    def get_data(self):
        self.data = eval(self.query('DATA?'))
    def get_exposure(self):
        return float(self.query('EXPTIME?'))
    def get_nb_frames(self):
        return int(self.query('NBFRAMES?'))
    def list_cameras(self):
        return self.query('LISTCAMS?')
    
    def enable_auto_exposure(self):
        self.write('AUTOEXPEN')
    def disable_auto_exposure(self):
        self.write('AUTOEXPDIS')
    def save_data_remote(self):
        self.write('SAVEDATA')
    def save_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_SPECTRO32{self.camera}.txt'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        self.lambd=[list(range(len(self.data[0])))]
        assert self.lambd, 'You may want to get_data before saving ...'
        [self.lambd.append(self.data[i]) for i in range(len(self.data))]
        f = savetxt(temp_filename,self.lambd)  ## squeeze
        print('Spectro32 data saved')


    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'exposure','type':float,'read':self.get_exposure,'write':self.set_exposure,'help':'Manage the camera exposure time'})
        model.append({'element':'variable','name':'nb_frames','type':int,'read':self.get_nb_frames,'write':self.set_nb_frames,'help':'Manage the number of frames to be acquired'})
        model.append({'element':'variable','name':'camera','type':str,'read':self.list_cameras,'write':self.set_camera,'help':'Manage cameras'})
        model.append({'element':'variable','name':'trace','type':ndarray,'read':self.get_data,'help':'Get the current trace in a numpy array'})
        model.append({'element':'action','name':'enable_auto_exposure','do':self.enable_auto_exposure,'help':'Enable auto exposure mode'})
        model.append({'element':'action','name':'disable_auto_exposure','do':self.disable_auto_exposure,'help':'Disable auto exposure mode'})
        return model


#################################################################################
############################## Connections classes ##############################
class Driver_SOCKET(Driver):
    def __init__(self,address='192.168.0.2',camera='Camera1',**kwargs):
        import socket 
        
        self.PORT        = 5005
        self.BUFFER_SIZE = 10000
        
        self.controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controller.connect((address,int(self.PORT)))
        
        Driver.__init__(self,camera,**kwargs)
        
    def write(self,command):
        self.controller.send(command.encode())
        self.recv_end(self.controller)
    def query(self,command):
        self.controller.send(command.encode())
        data = self.recv_end(self.controller)
        return data
    def recv_end(self,the_socket,end='\n'):
        total_data=[];data=''
        while True:
                data=the_socket.recv(self.BUFFER_SIZE).decode()
                if end in data:
                    total_data.append(data[:data.find(end)])
                    break
                total_data.append(data)
                if len(total_data)>1:
                    #check if end_of_data was split
                    last_pair=total_data[-2]+total_data[-1]
                    if end in last_pair:
                        total_data[-2]=last_pair[:last_pair.find(end)]
                        total_data.pop()
                        break
        return ''.join(total_data)
    def close(self):
        try :
            self.controller.close()
        except :
            pass
        self.controller = None

class Driver_LOCAL(Driver):
    def __init__(self,camera='Camera1',**kwargs):

        from spectro32_utilities.spectro32_driver import Driver
        self.controller = Driver()

        Driver.__init__(self,camera,**kwargs)
              
    def write(self,command):
        self.controller.command(command)
    def query(self,command):
        return self.controller.command(command)
    def close(self):
        self.controller = None
############################## Connections classes ##############################
#################################################################################


