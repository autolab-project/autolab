# -*- coding: utf-8 -*-

"""
Supported instruments (identified): MS2690A/MS2691A/MS2692A and
MS2830A/MS2840A/MS2850A
- Signal Analyzer
"""

# import time


class Driver() :
    """ This Driver contains only few functions available for this device """

    def __init__(self):
        self.write("SYST:LANG SCPI")  # force SCPI language to avoid errors
        self.write("inst spect")  # spectrum mode
        pass

    def get_id(self):
        return self.query('*IDN?')


    def get_frequency(self):
        return float(self.query("FREQ:CENT?"))*1e-9

    def set_frequency(self, value):
        value = float(value)*1e9
        self.write(f"FREQ:CENT {value}")
        self.query('*OPC?')


    def get_power_marker(self, marker_num):
        value = int(marker_num)
        return float(self.query(f"CALC:MARK{value}:Y?"))

    def get_power_marker_1(self):
        return self.get_power_marker(1)

    def get_power_marker_2(self):
        return self.get_power_marker(2)


    def repeat_sweep(self):
        self.write("INIT:CONT ON")

    def single_sweep(self):
    
        old_timeout = self.controller.timeout
        if old_timeout < 30000:
            self.controller.timeout = 30000
        self.write("INIT:CONT OFF")
        self.write("INIT:MODE:SING")
        # self.write("*WAI")
        self.query("*OPC?")
        self.controller.timeout = old_timeout

    def get_timeout(self):
        return float(self.controller.timeout)

    def set_timeout(self, value):
        value = float(value)
        self.controller.timeout = value
        

    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'frequency','unit':'GHz','read':self.get_frequency,'write':self.set_frequency,'type':float,'help':'Frequency of the signal in GHz'})
        model.append({'element':'variable','name':'power1','unit':'dBm','read':self.get_power_marker_1,'type':float,'help':'Power in dBm of the marker 1'})
        model.append({'element':'variable','name':'power2','unit':'dBm','read':self.get_power_marker_2,'type':float,'help':'Power in dBm of the marker 2'})
        model.append({'element':'action','name':'single_sweep','do':self.single_sweep,'help':'Start a single measurement'})
        model.append({'element':'action','name':'repeat_sweep','do':self.repeat_sweep,'help':'Start a single measurement'})

        model.append({'element':'variable','name':'timeout',
                      'read':self.get_timeout,'write':self.set_timeout,
                      'type':float,'unit':'s',
                      'help':'Change the controller timeout. Usefull if single measure too long'})
        return model

#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self,address='GPIB0::1::INSTR', **kwargs):
        import pyvisa as visa

        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = 3000

        Driver.__init__(self)

    def close(self):
        self.controller.close()
    def query(self,command):
        return self.controller.query(command).strip('\r\n')
    def write(self,command):
        self.controller.write(command)
############################## Connections classes ##############################
#################################################################################




