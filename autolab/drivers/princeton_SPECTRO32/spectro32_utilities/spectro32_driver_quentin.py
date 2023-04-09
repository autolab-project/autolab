# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 16:05:56 2020

@author: manip
"""
import ctypes as ct
import re
import numpy as np
import time
import copy 


class Driver() :
    
    def __init__(self,camera_name='Camera1'):
        
        # OPEN CAMERA
        # =====================================================================
        
        self.name = camera_name.encode('utf-8')
        self.hCam = ct.c_ushort()
        self.controller.pl_cam_open(ct.c_char_p(self.name),ct.byref(self.hCam), self.cst.OPEN_EXCLUSIVE)
        
        
        
        # SEQUENCE CONFIGURATION
        # =====================================================================
        
        # CCD Number of pixels in one line
        ccd_nb_pixels = ct.c_ushort()
        self.controller.pl_get_param(self.hCam, self.cst.PARAM_SER_SIZE, self.cst.ATTR_CURRENT, ct.byref(ccd_nb_pixels))
        ccd_nb_pixels = ccd_nb_pixels.value
        
        # CCD Number of lines
        ccd_nb_lines = ct.c_ushort()
        self.controller.pl_get_param(self.hCam, self.cst.PARAM_PAR_SIZE, self.cst.ATTR_CURRENT, ct.byref(ccd_nb_lines))
        ccd_nb_lines = ccd_nb_lines.value
        
        # Region
        self.region = Region( region_ref=[0, 0, ccd_nb_pixels-1, ccd_nb_lines-1], binning=[1, 1] )
        
        # Others parameters
        nb_exposures = ct.c_ushort(1)                       # 1 spectrum acquired each time
        nb_roi = ct.c_ushort(1)
        fake_exposure_time =  ct.c_uint(1)                  # ignored in variable_timed_mode
        exposure_mode = self.cst.VARIABLE_TIMED_MODE        # allow to change only the exposure time between two acquisition (see manual)
        stream_size = ct.c_uint()
        
        # Send configuration
        self.controller.pl_exp_setup_seq(self.hCam, nb_exposures, nb_roi, ct.byref(self.region), exposure_mode, fake_exposure_time, ct.byref(stream_size))



        # EXPOSURE TIME
        # =====================================================================
        
        # Unit (ms) 
        val = ct.c_short(self.cst.EXP_RES_ONE_MILLISEC)
        self.controller.pl_set_param(self.hCam, self.cst.PARAM_EXP_RES, ct.byref(val))
        
        # Initial value
        self.set_exposure_time(1)
        
        
        # OTHER INITIALIZATION STEPS
        # =====================================================================
        val = ct.c_short(self.cst.OPEN_PRE_SEQUENCE)
        self.controller.pl_set_param(self.hCam, self.cst.PARAM_SHTR_OPEN_MODE, ct.byref(val))
        val = ct.c_short(2)
        self.controller.pl_set_param(self.hCam, self.cst.PARAM_CLEAR_CYCLES, ct.byref(val))
        
        
        
    def get_temperature(self) :
        val = ct.c_short()
        self.controller.pl_get_param(self.hCam, self.cst.PARAM_TEMP, self.cst.ATTR_CURRENT, ct.byref(val))
        return val.value/100 # to get it in degrees
        
    def get_temperature_setpoint(self):
        val = ct.c_short()
        self.controller.pl_get_param(self.hCam, self.cst.PARAM_TEMP_SETPOINT, self.cst.ATTR_CURRENT, ct.byref(val))
        return val.value/100 # to get it in degrees
    
    


    def get_exposure_time(self):
        val = ct.c_ushort()
        self.controller.pl_get_param(self.hCam, self.cst.PARAM_EXP_TIME, self.cst.ATTR_CURRENT, ct.byref(val))
        return val.value
    
    def set_exposure_time(self,value):
        val = ct.c_ushort(value)
        self.controller.pl_set_param(self.hCam, self.cst.PARAM_EXP_TIME, ct.byref(val))
    
    
    
    
    def get_intensity(self):
        
    
        
        # START EXPOSURE SEQUENCE
        buf = np.empty((self.region.size()[1], self.region.size()[0]), dtype=np.uint16)
        self.controller.pl_exp_start_seq(self.hCam, buf.ctypes.data)   
        
        # WAIT FOR EXPOSURE SEQUENCE ENDING
        while True:
            status = ct.c_short()
            bcount = ct.c_uint()
            self.controller.pl_exp_check_status(self.hCam, ct.byref(status), ct.byref(bcount))
            if status.value in [self.cst.READOUT_COMPLETE, self.cst.READOUT_NOT_ACTIVE]:
                break
            else :
                time.sleep(0.01)
        
        # CONCLUDE EXPOSURE SEQUENCE
        # No working because attribute hbuf is missing, but I don't what it is
        # Maybe this function is just an optional post treatment of the data...
        # Perfectly working without
        #self.controller.pl_exp_finish_seq(self.hCam, self.buf.ctypes.data)
        
        return np.squeeze(buf)
    

        
    
    
class Driver_DLL(Driver):
    
    
    def __init__(self,masterfile=r'C:\Program Files\Princeton Instruments\PVCAM\SDK\master.h',
                     pvcamfile=r'C:\Program Files\Princeton Instruments\PVCAM\SDK\pvcam.h',**kwargs):
        
        # Load constants and associated values from the PVCAM files
        self.cst = PVCAMConstants([masterfile,pvcamfile])
        
        # Load and init the PVCAM library
        self.controller = ct.windll.Pvcam32        
        self.controller.pl_pvcam_init()
        self.controller.pl_exp_init_seq()
        
        Driver.__init__(self,**kwargs)


    def close(self):
        
        # Uninit the PVCAM Library
        self.controller.pl_pvcam_uninit()
        self.controller.pl_exp_uninit_seq()






class Region(ct.Structure):
    
    _fields_ = [
        ('s1', ct.c_ushort),
        ('s2', ct.c_ushort),
        ('sbin', ct.c_ushort),
        ('p1', ct.c_ushort),
        ('p2', ct.c_ushort),
        ('pbin', ct.c_ushort)
    ]
    
    def __init__(self, region_ref, binning):
        assert len(region_ref) == 4 
        assert len(binning) == 2 
        region = copy.copy(region_ref)
        region[2] = region_ref[0] + (int((region_ref[2]-region_ref[0])/binning[0]) * binning[0])
        region[3] = region_ref[1] + (int((region_ref[3]-region_ref[1])/binning[1]) * binning[1])
        ct.Structure.__init__(self, region[0], region[2], binning[0], region[1], region[3], binning[1])
            
    def size(self):
        return (int((self.s2-self.s1+1) / self.sbin), int((self.p2-self.p1+1) / self.pbin))





class PVCAMConstants :
    def __init__(self,paths) :
        self.paths = paths
        self.load()
        
    def decomment(self, string):
        return re.sub(r'/\*.*\*/', '', re.sub(r'//.*', '', string))
    
    def load(self):
        
        # For each file
        for path in self.paths:
            
            # Load raw content
            file = open(path)
            data = file.readlines()
            file.close()
            
            # For each line of that file
            for i in range(len(data)):
                
                # Clean that line
                line = self.decomment(data[i])
                
                # Search for #define, set variable
                m = re.match(r'\s*\#define\s+(\S+)\s+(.*)', line)
                if m is not None:
                    
                    var_name = m.groups()[0]
                    var_expr = m.groups()[1]
                    if len(var_name) > 0 and len(var_expr) > 0:
                        try:
                            exec(f'{var_name}={eval(var_expr)}')
                            exec(f'self.{var_name}={var_name}')
                        except :
                            pass
                        
                # search for enum
                if re.match(r'\s*enum\s+', line):
                    # concatenate lines until the end of the enum
                    ind = i
                    enum = ''
                    while True:
                        enum += self.decomment(data[ind])
                        if re.search('}', data[ind]):
                            break
                        ind += 1
                        
                    # Pull out variables
                    enum = re.sub('(\n|\s)', '', enum)
                    enum = re.sub(r'.*{', '', enum)
                    enum = re.sub(r'}.*', '', enum)
                    ind = 0
                    for var_name in enum.split(','):
                        setattr(self, var_name, ind)
                        ind += 1




