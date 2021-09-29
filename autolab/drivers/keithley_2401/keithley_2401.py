#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
Keithley 2400, 2401
-
"""



class Driver():

    def __init__(self):

        self.reset()

    def reset(self):
        self.write('*CLS')
        self.write(":form:elem curr")  # tell the smu to read only currents values
        self.write(":SOURce:func VOLT")  # set SMU as volt generator
        # self.write(":SOURce:VOLTage:MODE FIXed")  # set DC source
        # self.write(":SENSe:CURRent:RANGe:AUTO True")  # Control auto ranging for amps
        # self.write(":SENSe:VOLTage:RANGe:AUTO True")  # Control auto ranging for volts
        self.write(":DISPlay:ENABle ON")

    def get_range(self):
        return float(self.query(f":sour:volt:rang?"))

    def set_range(self, value):
        value = float(value)
        self.write(f":SOURce:VOLTage:RANGe {value}")

    def get_current(self):
    # not supposed to use single shot if want to keep voltage set after
        # return float(self.query(f'MEASure:CURRent?'))  # Do one shot measurement (test if this line stop the measurement)

        if self.get_output_state() is False:
            self.set_output_state(True)

        return float(self.query("READ?"))  # do INIT to measurement and read then read data. need the SMU in source volt (should read from buffer in a continious measurment config)
        # return float(self.query("FETCh?"))  # get data from buffer without doing masurements. need the SMU in source volt (should read from buffer in a continious measurment config)

    def get_current_compliance(self):
        return float(self.query(f':CURRent:PROTection:LEVel?'))

    def set_current_compliance(self,value):
        value = float(value)
        self.write(f':CURRent:PROTection {value}')

    def get_voltage(self):
        return float(self.query(f":SOURce:VOLTage:LEVel?"))

    def set_voltage(self, value):
        value = float(value)
        self.write(f":SOURce:VOLTage:LEVel {value}")
        self.query('*OPC?')
        if self.get_output_state():
            self.query("READ?")  # Used to correctly apply the voltage due to the compliance limitation

    def get_output_state(self):
        ans = self.query(f"OUTPut?")
        return bool(int(float(ans)))

    def set_output_state(self,state):
        state = bool(int(float(state)))
        if state is True:
            self.write(f"OUTPut ON")
            self.query("READ?")  # Used to correctly apply the voltage due to the compliance limitation
        else:
            self.write(f"OUTPut OFF")

    def get_id(self):
        return self.query('*IDN?')

    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'current','unit':'A','read':self.get_current,'type':float,'help':'Current at the output as measured (read only)'})
        model.append({'element':'variable','name':'current_compliance','unit':'A','read':self.get_current_compliance,'write':self.set_current_compliance,'type':float,'help':'Current compliance'})
        model.append({'element':'variable','name':'voltage','unit':'V','read':self.get_voltage,'write':self.set_voltage,'type':float,'help':'Set voltage or read previous set voltage'})
        model.append({'element':'variable','name':'range','unit':'V','read':self.get_range,'write':self.set_range,'type':float,'help':'Set voltage range or read it'})
        model.append({'element':'variable','name':'output','read':self.get_output_state,'write':self.set_output_state,'type':bool,'help':'Output state (on/off), passed as boolean to the function: True/False'})
        return model


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):

    def __init__(self, address='GPIB0::22::INSTR',**kwargs):
        import pyvisa as visa

        self.TIMEOUT = 5000 #ms
        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.TIMEOUT

        Driver.__init__(self)


    def close(self):
        try:
            self.controller.close()
        except:
            pass

    def query(self, command):
        result = self.controller.query(command)
        result = result.strip('\n')
        return result
    def write(self,command):
        self.controller.write(command)
    def read(self):
        result = self.controller.read()
        return result.strip('\n')


class Driver_GPIB(Driver):

    def __init__(self,address=0,board_index=22,**kwargs):
        import Gpib

        self.inst = Gpib.Gpib(int(board_index),int(address))
        Driver.__init__(self, **kwargs)

    def query(self,query):
        self.write(query)
        return self.read()

    def write(self,command):
        self.inst.write(command)

    def read(self,length=1000000000):
        return self.inst.read(length).decode().strip('\r\n')

    def close(self):
        """WARNING: GPIB closing is automatic at sys.exit() doing it twice results in a gpib error"""
        #Gpib.gpib.close(self.inst.id)
        pass
############################## Connections classes ##############################
#################################################################################


