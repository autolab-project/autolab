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
        self.buffer = 0

    def chronometer(self):
        return time.time() - self.chronometer_startTime

    def reset_chronometer(self):
        self.chronometer_startTime = time.time()

    def get_paramter_buffer(self):
        return self.buffer

    def parameter_buffer(self,value):
        self.buffer = value

    def wait(self,delay):
        time.sleep(delay)


    def get_default_dir(self):
        return str(os.getcwd())

    def set_default_dir(self, folder):
        os.chdir(str(folder))


    def create_folder(self, folder_name):
        os.makedirs(folder_name)


    def get_driver_model(self):

        model = []
        model.append({'element':'variable','name':'chronometer','type':float,'read':self.chronometer,'unit':'s','help':'Elapsed time since chronometer reset'})
        model.append({'element':'action','name':'reset_chronometer','do':self.reset_chronometer,'help':'Reset the chronometer time'})
        model.append({'element':'variable','name':'parameter_buffer','type':float,'read':self.get_paramter_buffer,'write':self.parameter_buffer,'help':'Parameter buffer for monitoring in the scanning panel. Can read this value'})
        model.append({'element':'action','name':'wait','param_type':float,'param_unit':'s','do':self.wait,'help':'System wait during the value provided.'})
        model.append({'element':'variable','name':'default_dir',
                      'read':self.get_default_dir, 'write':self.set_default_dir,
                      "type":str,'help':'Change the default path'})
        model.append({'element':'action','name':'create_folder',
                      'do':self.create_folder,
                      "param_type":str,'help':'Create a folder'})


        return model



#################################################################################
############################## Connections classes ##############################
class Driver_DEFAULT(Driver):
    def __init__(self):

        Driver.__init__(self)


############################## Connections classes ##############################
#################################################################################
