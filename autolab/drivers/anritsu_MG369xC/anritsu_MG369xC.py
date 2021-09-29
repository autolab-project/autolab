# -*- coding: utf-8 -*-

"""
Supported instruments (identified): Anritsu MG369xC
- Synthesized Signal Generators
Note: use the SCPI manual and not the GPIB
"""

ADDRESS = 'GPIB0::5::INSTR'


class Driver() :

    def __init__(self):
        pass

    def get_id(self):
        return self.query('*IDN?')

    def wait(self):
        self.write("*WAI")

    def set_remote(self, state):
        value = bool(state)
        self.write("REN") if value else self.write("RL")  # rl doesn't work

    def get_output_state(self):
        ans = self.query(":OUTP:STAT?")
        return bool(int(ans))

    def set_output_state(self, state):
        value = "ON" if state else "OFF"
        self.write(f":OUTP:STAT {value}")
        self.query('*OPC?')  # TODO: check if work
        # self.wait()  # TODO: see if needed or not

    def get_frequency(self):
        return float(self.query(":freq:CW?"))*1e-9

    def set_frequency(self, value):
        self.write(f":freq:CW {float(value)} GHz")
        self.query('*OPC?')

    def get_power(self):
        return float(self.query(":power?"))

    def set_power(self, value):
        self.write(f":power {float(value)} dBm")
        self.query('*OPC?')

    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'frequency','unit':'GHz','read':self.get_frequency,'write':self.set_frequency,'type':float,'help':'Set the frequency of the signal in GHz'})
        model.append({'element':'variable','name':'power','unit':'dBm','read':self.get_power,'write':self.set_power,'type':float,'help':'Set the power in dBm'})
        model.append({'element':'variable','name':'output','read':self.get_output_state,'write':self.set_output_state,'type':bool,'help':'Output state (on/off), passed as boolean to the function: True/False'})

        return model

#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self,address=ADDRESS, **kwargs):
        import pyvisa as visa

        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)

        Driver.__init__(self)

    def close(self):
        self.set_remote(False)
        self.controller.close()
    def query(self,command):
        return self.controller.query(command)
    def write(self,command):
        self.controller.write(command)

############################## Connections classes ##############################
#################################################################################
