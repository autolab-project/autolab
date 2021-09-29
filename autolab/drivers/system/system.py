#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


import time 
import os


class Driver():
        
    def __init__(self):
        pass
        self.chronometer_startTime = time.time()
    
    def chronometer(self):
        return time.time() - self.chronometer_startTime
    
    def reset_chronometer(self):
        self.chronometer_startTime = time.time()
        
    def parameter_buffer(self,value):
        pass
    
    def wait(self,delay):
        time.sleep(delay)
    

    def get_default_dir(self):
        return str(os.getcwd())

    def set_default_dir(self, folder):
        os.chdir(str(folder))


    def create_folder(self, folder_name):
        os.mkdir(folder_name)

    def create_folder_cascade(self, folder_name):

        drive, path = os.path.splitdrive(folder_name)

        folders = []
        folder = "temp"
        while folder != "":
            folders.append(os.path.join(drive, path))
            path, folder = os.path.split(path)

        folders.reverse()

        if folders[0] == "":
            folders.pop(0)

        errors = list()
        for folder in folders:
            try:
                os.mkdir(folder)
            except PermissionError:
                pass
            except FileExistsError:
                pass
            except Exception as error:
                errors.append(error)

        if len(errors) != 0:
            raise Exception(str(errors))


    def get_driver_model(self):
        
        model = []
        model.append({'element':'variable','name':'chronometer','type':float,'read':self.chronometer,'unit':'s','help':'Elapsed time since chronometer reset'})
        model.append({'element':'action','name':'reset_chronometer','do':self.reset_chronometer,'help':'Reset the chronometer time'})
        model.append({'element':'variable','name':'parameter_buffer','type':float,'write':self.parameter_buffer,'help':'Parameter buffer for monitoring in the scanning panel. Does nothing with the input value'})
        model.append({'element':'action','name':'wait','param_type':float,'param_unit':'s','do':self.wait,'help':'System wait during the value provided.'})
        model.append({'element':'variable','name':'default_dir',
                      'read':self.get_default_dir, 'write':self.set_default_dir,
                      "type":str,'help':'Change the default path'})
        model.append({'element':'action','name':'create_folder',
                      'do':self.create_folder,
                      "param_type":str,'help':'Create a folder'})
        model.append({'element':'action','name':'create_folder_cacade',
                      'do':self.create_folder_cascade,
                      "param_type":str,'help':'Create all the folders in the string'})

        return model
        
        
    
#################################################################################
############################## Connections classes ##############################
class Driver_DEFAULT(Driver):
    def __init__(self):
        
        Driver.__init__(self)
        

############################## Connections classes ##############################
#################################################################################
