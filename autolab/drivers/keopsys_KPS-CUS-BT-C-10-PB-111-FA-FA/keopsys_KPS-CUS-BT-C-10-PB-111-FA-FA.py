#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- Keopsys
KPS-CUS-BT-C-10-PB-111-FA-FA
CYFA-PB/BO
CEFA-L-PB-LP
CEFA-C-BO-HP
CEFA-C-PB-HP
CEFA-L-WDM-HP
CEFA-L-HG
CTFA-PB
"""

import time


class Driver() :

    def __init__(self):
        # self._STATE = False
        # self.set_output_state(False)
        pass

    def wait(self, value=0.03):
        time.sleep(value)

    def get_id(self):
        return self.query('*IDN?')


    def get_power(self):
        self.wait() # needed to avoid error of reading to early
        return float(self.query('CPU?').split('=')[1])/10

    def set_power(self, value):
        value = int(round(value*10))
        self.write("CPU="+str(value))


    def get_input_power(self):
        self.wait()
        return float(self.query('PUE?').split('=')[1])/100

    def get_output_power(self):
        self.wait()
        return float(self.query('PUS?').split('=')[1])/100

    def get_current1(self):
        self.wait()
        return int(self.query("IC1?").split('=')[1])

    def get_real_current1(self):
        self.wait()
        return int(self.query("ID1?").split('=')[1])

    def set_current1(self, value):
        value = int(value)
        self.write(f"IC1={value}")

    def get_current2(self):
        self.wait()
        return int(self.query("IC2?").split('=')[1])

    def get_real_current2(self):
        self.wait()
        return int(self.query("ID2?").split('=')[1])

    def set_current2(self, value):
        value = int(value)
        self.write(f"IC2={value}")

    # def get_gain(self):
    #     # BUG: not compatible with cefa c pb hp and other
    #     # it is a consign gain not a measured one
    #     # return float(
    #         return self.query('CGA?')
    #     # .split('=')[1]/100)

    # def get_nominal_output_power(self):
    #     # not compatible with my edfa (kps)
    #     # return float(
    #         return self.query('PNO?')
    # # .split('=')[1])

    def get_alarms_bits(self):
        self.wait()
        exa = str(self.query("ALA?").split('=')[1])  # 4 exa numbers -> 16 alarms
        bits = format(int(exa, 16), 'b')  # convert exa to bit
        bits = "0"*(16-len(bits)) + str(bits)  # add 0 at begin of string to have all 16 bits
        bits = list(bool(int(x)) for x in bits[::-1])  # convert string to bool and set each bits in a list with the bit number as the list index

        return bits  # if want to know the state of the bit 12: bits[12]

    def get_alarms(self):
        bits = self.get_alarms_bits()

        alarms = ["Temperature control of the first diode is out or range",
                  "Temperature control of the second diode is out of range",
                  "Reset",
                  "Key OFF",
                  "Temperature control off (T<15°C or T>40°C)",
                  "First diode current is too high",
                  "Diode current is too low (<25mA)",
                  "Second diode current is too high",
                  "Temperature of the first diode under set value (16°C)",
                  "Temperature of the first diode is above set value (39°C)",
                  "Temperature of the second diode is under set value (16°C)",
                  "Temperature of the second diode is above set value (39°C)",
                  "Temperature of the board is above set value (63°C)",
                  "Loss of input power",
                  "Loss of output power",
                  "Laser off",
                  ]

        alarms_active = list()

        for alarm, bit in zip(alarms, bits):
            if bit:
                alarms_active.append(alarm)

        return alarms_active

    def display_alarms(self):
        return str(self.get_alarms())


    def get_mode_state(self):
        self.wait()
        ans = int(self.query('ASS?').split('=')[1])
        return ans
        # if ans == 0:
        #     return "OFF"
        # elif ans == 1:
        #     return "ACC"
        # elif ans == 2:
        #     return "APC"
        # elif ans == 4:
        #     return "AGC"
        # else:
        #     raise ValueError("Unknown value get from output state:", ans)


    def set_mode_state(self, value):
        value = int(value)
        self.write(f"ASS={value}")
        self.wait()

    def get_output_state(self):
        self.wait(1)
        bits = self.get_alarms_bits()
        laser_off_bit = bool(bits[15])
        state = not laser_off_bit # bit nbr 15 = 1 if laser off
        return state


    def set_output_state(self, state):
        self.wait(0.2)  # Doesn't set the state if still doing something before
        value = int(state)
        self.write(f"K{value}")  # K0 or K1
        self.wait(0.3)  # Necessary


    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'power',
                      'read':self.get_power,'write':self.set_power,
                      'type':float,'unit':'dBm',
                      'help':'Set output power.'})
        model.append({'element':'variable','name':'input_power',
                      'read':self.get_input_power,
                      'type':float,'unit':'dBm',
                      'help':'Get input power of the EDFA.'})
        model.append({'element':'variable','name':'output_power',
                      'read':self.get_output_power,
                      'type':float,'unit':'dBm',
                      'help':'Get real output power of the EDFA.'})
        model.append({'element':'variable','name':'alarms',
                      'read':self.display_alarms,
                      'type':str,
                      'help':'Display the active alarms.'})
        # model.append({'element':'variable','name':'gain','type':float,'read':self.get_gain, 'help':'Get EDFA gain.'})
        # model.append({'element':'variable','name':'nominal_output_power','type':float,'read':self.get_nominal_output_power, 'help':'Get EDFA nominal power.'})
        model.append({'element':'variable','name':'output',
                      'read':self.get_output_state,'write':self.set_output_state,
                      'type':bool,
                      'help':'Set EDFA output state.'})

        model.append({'element':'variable','name':'current1_setpoint',
                      'read':self.get_current1,"write":self.set_current1,
                      'type':int,'unit':'mA',
                      'help':'Get first diode current.'})
        model.append({'element':'variable','name':'current1',
                      'read':self.get_real_current1,
                      'type':int,'unit':'mA',
                      'help':'Get first diode current.'})

        model.append({'element':'variable','name':'current2_setpoint',
                      'read':self.get_current2,"write":self.set_current2,
                      'type':int,'unit':'mA',
                      'help':'Get second diode current.'})
        model.append({'element':'variable','name':'current2',
                      'read':self.get_real_current2,
                      'type':int,'unit':'mA',
                      'help':'Get second diode current.'})

        model.append({'element':'variable','name':'mode','type':int,'read':self.get_mode_state,'write':self.set_mode_state,'help':'Set EDFA mode state. (Work only if the key is turn off)'})
        return model

#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR', **kwargs):
        import pyvisa as visa

        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.write_termination = 0x00  #needed in order to read properly from the optical amplifier
        self.controller.read_termination = 0x00

        Driver.__init__(self)

    def close(self):
        self.write("GTL")
        self.controller.close()

    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\x00')
        return result

    def write(self,command):
        self.controller.write(command)
############################## Connections classes ##############################
#################################################################################