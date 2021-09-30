#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- MS9710B
"""


class Driver() :

    def __init__(self):

        self.data = []  # become pandas.DataFrame
        self._set_device_var()


    def _set_device_var(self):
        device_id = self.get_id()  # "Anritsu,MS9740A,6200123456,1.00.00"
        device_name_list = ("MS9710B", "MS9710C", "MS9740A", "MS9740B")  # order is important if find only part of string

        for device_name in device_name_list:
           if str(device_id).upper().find(device_name) != -1:
               break  # if don't find device, take newest device

        getattr(self, f"_{device_name}_variables")()


    # do MS9703A = MV02 ? older than MS9710B

    def _MS9710B_variables(self):
        self.allowed_points = (51,101,251,501,1001,2001,5001)
        self.allowed_res = (0.07, 0.1, 0.2, 0.5, 1)
        self.allowed_vbw = (10, 100, 1000, 10000, 100000, 1000000)

    def _MS9710C_variables(self):
        self.allowed_points = (51,101,251,501,1001,2001,5001)
        self.allowed_res = (0.05, 0.07, 0.1, 0.2, 0.5, 1)
        self.allowed_vbw = (10, 100, 1000, 10000, 100000, 1000000)

    def _MS9740A_variables(self):
        self.allowed_points = (51,101,251,501,1001,2001,5001,10001,20001,50001)
        self.allowed_res = (0.03, 0.05, 0.07, 0.1, 0.2, 0.5, 1)
        self.allowed_vbw = (10, 100, 200, 1000, 2000, 10000, 100000, 1000000)
        # could set function/unit depending on device
        
    def _MS9740B_variables(self):
        self._MS9740A_variables()
        
    def _set_closest(self, allowed_list, value):
        a = allowed_list
        index = min(range(len(a)), key=lambda i: abs(a[i]-value))
        return a[index]

    def _get_unit(self, value):
        import re
        pattern = re.compile('[\W\d_]+')
        unit = pattern.sub('', str(value)).upper()
        return unit

    def _remove_unit(self, value):
        unit = str(self._get_unit(value))
        value = str(value).upper().rstrip(unit.upper())

        return value

    def _apply_unit(self, value):
        """ value = -1.23UNIT"""
        unit_conversion = {"HZ": 1, "KHZ": 1e3, "MHZ": 1e6, "GHZ": 1e9,
                           }
        unit_list = tuple(unit_conversion.keys())
        unit = str(self._get_unit(value))
        value = float(self._remove_unit(value))

        if unit in unit_list:
            value *= unit_conversion[unit]
        return value


    def get_id(self):
        return self.query('*IDN?')

    def opc(self):
        self.query('*OPC?')


    def get_resol(self):
        return float(self.query('RES?'))  # nm

    def set_resol(self,value):
        value = float(self._set_closest(self.allowed_res, value))
        self.write(f'RES {value}')
        self.opc()

    def get_span(self):
        return float(self.query('SPN?'))  # nm

    def set_span(self, value):
        value = float(value)
        self.write(f'SPN {value}')
        self.opc()


    def get_vbw(self):
        ans = self.query('VBW?')  # example: 10MHZ
        value = int(self._apply_unit(ans))  # example: 1e7
        return float(value)

    def set_vbw(self, value):
        value = self._apply_unit(value)  # useless because must be float in GUI
        value = int(self._set_closest(self.allowed_vbw, value))
        self.write(f'VBW {value}')
        self.opc()

    def get_nbpts(self):
        return(int(self.query("MPT?")))

    def set_nbpts(self, value):
        value = int(self._set_closest(self.allowed_points, value))
        self.write(f"MPT {value}")
        self.opc()


    def get_wavelength_center(self):
        return float(self.query("CNT?"))

    def set_wavelength_center(self, value):
        self.write(f"CNT {value}")
        self.opc()


    def get_wavelength_start(self):
        return float(self.query("STA?"))

    def set_wavelength_start(self, value):
        value = float(value)
        self.write(f"STA {value}")
        self.opc()


    def get_wavelength_stop(self):
        return float(self.query("STO?"))

    def set_wavelength_stop(self, value):
        value = float(value)
        self.write(f"STO {value}")
        self.opc()


    def get_peak_state(self):
        return str(self.query("PKS?"))  #output "PEAK", "NEXT"...)

    def search_peak(self):
        self.write("PKS PEAK")
        self.opc()

    def search_peak_next(self):
        self.write("PKS NEXT")
        self.opc()

    def search_peak_last(self):
        self.write("PKS LAST")
        self.opc()

    def search_peak_left(self):
        self.write("PKS LEFT")
        self.opc()

    def search_peak_right(self):
        self.write("PKS RIGHT")
        self.opc()

    def _get_trace_marker(self):   # value off search peak
        ans = self.query("TMK?")
        wl, power = ans.split(",")
        wl = float(wl)

        power = float(self._remove_unit(power))  # could have get_unit if needed

        return (wl, power)

    def get_trace_wavelength(self):
        return self._get_trace_marker()[0]  # nm or THz

    def set_trace_wavelength(self, value):
        value = float(value)
        self.write(f"TMK {value}")
        self.opc()

    def get_trace_power(self):
        return self._get_trace_marker()[1]


    def get_marker_a(self):
        return float(self.query("MKA?"))

    def get_marker_b(self):
        return float(self.query("MKB?"))

    def get_marker_c(self):  # use this if want threshold 3dB then A, B , C, D to have all wl and power in rectangular -3dB
        ans = self.query("MKC?")
        value = self._remove_unit(ans)
        return float(value)

    def get_marker_d(self):
        ans = self.query("MKD?")
        value = self._remove_unit(ans)
        return float(value)


    def get_search_spectrum_power_state(self):
        text = self.query("ANA?")
        state = True if text == "PWR" else False
        return state

    def set_search_spectrum_power_state(self, value):
        state = bool(int(float(value)))
        text = "PWR" if state else "OFF"
        self.write(f"ANA {text}")
        self.opc()

    def _get_spectrum_marker(self):
        ans = self.query("ANAR?").split(",")
        if ans[0] == "":
            power = -999.9
            wl = 0
        else:
            power = float(ans[0])
            wl = float(ans[1])
        return (wl, power)

    def get_spectrum_power(self):
        return float(self._get_spectrum_marker()[1])

    def get_spectrum_wavelength(self):
        return float(self._get_spectrum_marker()[0])


    def erase_markers(self):
        self.write("EMK")
        self.opc()


    def get_data(self):  # very slow, need more timeout
        from numpy import linspace
        from pandas import DataFrame

        if self.TIMEOUT < 20000:
            self.controller.timeout = 20000
        power = self.query("DMA?").split("\r\n") # DMA or DMB
        self.controller.timeout = self.TIMEOUT
        power = [float(point) for point in power]

        wl_start, wl_stop, points = self.get_condition()
        wl = linspace(float(wl_start), float(wl_stop), int(points))

        data = DataFrame()
        data["wl"] = wl
        data["power"] = power

        self.data = data

        return data

    def save_data(self, filename):
        if len(self.data) != 0:
            self.data.to_csv(filename, index=False)

    def get_condition(self, trace="A"):
        wl_start, wl_stop, points = self.query(f"DC{trace}?").split(",")
        wl_start, wl_stop, points = float(wl_start), float(wl_stop), int(points)
        return (wl_start, wl_stop, points)


    def single_sweep(self):
        self.write('SSI')
        self.opc()  # OPTIMIZE: don't tell when scan if over but only when command is sended
        # could use SRQ like example in pdf

    def repeat_sweep(self):
        self.write('SRT')
        self.opc()

    def stop_sweep(self):
        self.write('SST')
        self.opc()



    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'resolution',
                      'write':self.set_resol,'read':self.get_resol,
                      'type':float, 'unit':'nm',
                      'help':"Resolution (nm)"})
        model.append({'element':'variable','name':'span',
                      'write':self.set_span,'read':self.get_span,
                      'type':float, 'unit':'nm',
                      'help':"Span (nm)"})
        model.append({'element':'variable','name':'vbw',
                      'write':self.set_vbw,'read':self.get_vbw,
                      'type':int, 'unit':"Hz",
                      'help':"Video Bandwitdh (Hz)"})
        model.append({'element':'variable','name':'points',
                      'write':self.set_nbpts,'read':self.get_nbpts,
                      'type':int,
                      'help':"How many points"})
        model.append({'element':'variable','name':'wavelength_center',
                      'write':self.set_wavelength_center,'read':self.get_wavelength_center,
                      'type':float,'unit':'nm',
                      'help':"Center wavelength (nm)"})
        model.append({'element':'variable','name':'wavelength_start',
                      'write':self.set_wavelength_start,'read':self.get_wavelength_start,
                      'type':float,'unit':'nm',
                      'help':"Start wavelength (nm)"})
        model.append({'element':'variable','name':'wavelength_stop',
                      'write':self.set_wavelength_stop,'read':self.get_wavelength_stop,
                      'type':float,'unit':'nm',
                      'help':"Stop wavelength (nm)"})
        model.append({'element':'variable','name':'trace_wavelength',
                      'write':self.set_trace_wavelength,'read':self.get_trace_wavelength,
                      'type':float, "unit":"nm",
                      'help':"Trace wavelength (nm)"})
        model.append({'element':'variable','name':'trace_power',
                      'read':self.get_trace_power,
                      'type':float,
                      'help':"Trace power"})
        model.append({'element':'variable','name':'spectrum_power',
                      'read':self.get_spectrum_power,
                      'type':float,
                      'help':"Spectrum power"})
        model.append({'element':'variable','name':'spectrum_wavelength',
                      'read':self.get_spectrum_wavelength,
                      'type':float, "unit":"nm",
                      'help':"Spectrum wavelength (nm)"})

        model.append({'element':'action','name':'search_peak',
                      'do':self.search_peak,
                      'help':"Search peak"})
        model.append({'element':'action','name':'search_peak_next',
                      'do':self.search_peak_next,
                      'help':"Search peak next"})
        model.append({'element':'action','name':'search_peak_last',
                      'do':self.search_peak_last,
                      'help':"Search peak last"})
        model.append({'element':'action','name':'search_peak_left',
                      'do':self.search_peak_left,
                      'help':"Search peak left"})
        model.append({'element':'action','name':'search_peak_right',
                      'do':self.search_peak_right,
                      'help':"Search peak right"})
        model.append({'element':'variable','name':'search_spectrum_power',
                      'read':self.get_search_spectrum_power_state,'write':self.set_search_spectrum_power_state,
                      'type':bool,
                      'help':"Set search spectrum power ON/OFF"})
        model.append({'element':'action','name':'single_sweep',
                      'do':self.single_sweep,
                      'help':"Perform a single sweep"})
        model.append({'element':'action','name':'repeat_sweep',
                      'do':self.repeat_sweep,
                      'help':"Perform sweep in continue"})
        model.append({'element':'action','name':'stop_sweep',
                      'do':self.stop_sweep,
                      'help':"Stop sweep"})
        model.append({'element':'action','name':'get_data',
                      'do':self.get_data,
                      'help':"Get sweep data"})
        model.append({'element':'action','name':'save_data',
                      'do':self.save_data,
                      "param_type":str,
                      'help':"Save stored sweep"})
        model.append({'element':'action','name':'erase_markers',
                      'do':self.erase_markers,
                      'help':"Erase markers"})






        return model

#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self,address='GPIB0::1::INSTR', **kwargs):
        import pyvisa as visa

        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)

        self.TIMEOUT = 5000  # ms
        self.controller.timeout = self.TIMEOUT

        Driver.__init__(self)

    def close(self):
        self.controller.close()
    def query(self,command):
        return self.controller.query(command).strip('\r\n')
    def write(self,command):
        self.controller.write(command)
############################## Connections classes ##############################
#################################################################################





