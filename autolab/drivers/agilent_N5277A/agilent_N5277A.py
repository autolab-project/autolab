# -*- coding: utf-8 -*-

"""
Supported instruments (identified): N5277A
- Vector Network Analyzer
"""

import os
import time


class Driver:
    r"""
    self.write(":CALCulate1:FORMat MLOG")
    self.write("Display:WINDow1:TRACe1:Y:Scale:AUTO")

    # BUG: if don't do get_trace, markers and maybe other feature can't be found -> either put a get in each function or user must get himself
    """

    def __init__(self):
        
        self.data = Data(self)
        self.display = Display(self)
        self.average = Average(self)
        self.sweep = Sweep(self)
        self.frequency = Frequency(self)
        self.trigger = Trigger(self)
        self.power = Power(self)
        self.markers = Markers(self)
        self.macro = Macro(self)
        
        #L change default path form c:\users\public\documents\Network analyzer\Documents'  to:
        new_default_path = 'C:/Users/PNA-ADMIN/Desktop/default'
        self.data.create_folder_cascade(new_default_path)
        self.data.set_default_dir(new_default_path)


    ## INTERNAL ##
    def get_id(self):
        return self.query('*IDN?')

    def wait(self):
        self.write("*WAI")  # tell the device to wait the previous command to finish before going to the next. But, controller can still send new commands that will bu queue

    def opc(self):
        self.query("*OPC?")  # stop the controller until all commands in the device queue are executed

    def clear(self):
        self.write("*CLS")  # clear status

    def abort(self):
        self.write("ABORT")


    ## CONFIG ##
    def config(self):
        self.preset()
        self.display.set_display(True)
        self.display.add_s11()
        self.display.add_s21()
        self.display.add_s41()
        self.wait()

    def config2(self):  # can use mutiple wwindows but stay with 1 for now
        self.preset()
        self.write("CALCulate1:PARameter:DEFine:EXT 'Meas1','S11'")
        self.write("CALCulate2:PARameter:DEFine:EXT 'Meas2','S21'")
        self.write("DISPlay:WINDow1:STATE ON")
        self.write("DISPlay:WINDow2:STATE ON")
        self.write("DISPlay:WINDow1:TRACe1:FEED 'Meas1'")
        self.write("DISPlay:WINDow2:TRACe2:FEED 'Meas2'")
        self.write("SENSe1:FREQuency:SPAN 1e9")
        self.write("SENSe2:FREQuency:SPAN 2e9")
        self.write("CALCulate1:PARameter:SELect 'Meas1'")
        self.write("CALCulate2:PARameter:SELect 'Meas2'")
        self.write("CALCulate1:MARKer:STATe ON")
        self.write("CALCulate2:MARKer:STATE ON")


    def get_timeout(self):
        return float(self.controller.timeout)

    def set_timeout(self, value):
        value = float(value)
        self.controller.timeout = value


    ## PRESET ##
    def preset(self):
        self.write("SYST:FPReset")


    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'timeout',
                      'read':self.get_timeout,'write':self.set_timeout,
                      'type':float,'unit':'s',
                      'help':'Change the controller timeout. Usefull if single measure too long'})

        model.append({'element':'action','name':'preset','do':self.preset,'help':'Preset the PNA'})
        model.append({'element':'action','name':'config','do':self.config,'help':'Do config'})
        model.append({'element':'action','name':'config_demo','do':self.config2,'help':'Do config_demo'})
        model.append({'element':'action','name':'abort','do':self.abort,'help':'Abort'})
        model.append({'element':'action','name':'opc','do':self.opc,'help':'opc'})
        # model.append({'element':'action','name':'wait','do':self.wait,'help':'wait'})

        model.append({'element':'module','name':'data','object':getattr(self,'data')})
        model.append({'element':'module','name':'markers','object':getattr(self,'markers')})
        model.append({'element':'module','name':'frequency','object':getattr(self,'frequency')})
        model.append({'element':'module','name':'sweep','object':getattr(self,'sweep')})
        model.append({'element':'module','name':'power','object':getattr(self,'power')})
        model.append({'element':'module','name':'average','object':getattr(self,'average')})
        model.append({'element':'module','name':'display','object':getattr(self,'display')})
        model.append({'element':'module','name':'trigger','object':getattr(self,'trigger')})
        model.append({'element':'module','name':'macro','object':getattr(self,'macro')})

        return model


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self,address='GPIB0::16::INSTR', **kwargs):
        import pyvisa as visa

        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)

        # self.TIMEOUT = 5000 #ms
        # self.controller.timeout = self.TIMEOUT

        Driver.__init__(self)

    def close(self):
        self.controller.close()

    def query(self,command):
        return self.controller.query(command).strip('\n')

    def write(self,command):
        self.controller.write(command)
############################## Connections classes ##############################
#################################################################################


## All the PNA submodules ##


class Macro:

    def __init__(self, dev):
        self.query = dev.query
        self.write = dev.write
        
    def get_macro_title(self, value):
        value = int(value)
        return str(self.query(f"SYST:SHOR{value}:TITLe?"))

    def get_macro_list(self):
        return [str(self.get_macro_title(x)) for x in range(1, 25)]

    def exec_macro_title(self, value):
        value = str(value)
        macro_list = self.get_macro_list()

        for i, macro in enumerate(macro_list):
            if macro == f'"{value}"':
                num = i+1
                break
        else:
            raise NameError(f"Can't find the macro {value}")

        self.exec_macro_num(num)

    def exec_macro_num(self, value):
        value = int(value)
        self.write(f"SYST:SHOR{value}:EXEC")


    def get_driver_model(self):
        model = []

        model.append({'element':'action','name':'exec_macro_num',
                      'do':self.exec_macro_num,
                      'param_type':int,'help':'Execute the macro with the given number'})
        model.append({'element':'action','name':'exec_macro_title',
                      'do':self.exec_macro_title,
                      'param_type':str,'help':'Execute the macro with the given title. Example: "LCA"'})

        return model


class Display:

    def __init__(self, dev):

        self.query = dev.query
        self.write = dev.write

    ## DISPLAY andd TRACES ##
    def get_window_state(self):
        return bool(int(float(self.query("DISPlay:WINDow1:STATE?"))))

    def set_window_state(self, value):
        state = int(bool(int(float(value))))
        self.write(f"DISPlay:WINDow1:STATE {state}")


    def get_display(self):
        return bool(int(float(self.query("DISP:ENAB?"))))

    def set_display(self, value):
        """Disable the display to have faster acquisition"""
        state = int(bool(int(float(value))))
        self.write(f"DISP:ENAB {state}")


    def get_trace(self):
        self.select_trace()  # get the currently displayed trace
        return int(self.query("CALC:PAR:MNUM?")) # tell the trace number

    def select_trace(self):
        chan = int(self.get_active_channel())
        meas = str(self.get_active_measurement())
        self.write(f"CALC{chan}:PAR:SEL {meas}") # send 'CALC1:PAR:SEL "MyS41"'

    def set_trace(self, value):
        value = int(value)
        self.write(f"CALC:PAR:MNUM {value}")


    def get_active_channel(self):
        return int(self.query("SYST:ACT:CHAN?"))

    def get_active_measurement(self):
        return str(self.query("SYST:ACT:MEAS?"))  # return 'CH1_S11_1'



    def add_s11(self):
        self.set_window_state(True)  # faster to set always true even if already open than asking if open before openning it if closed
        self.write("CALCulate:PARameter:DEFine:EXT 'CH1_S11',S11")  # Define a measurement name, parameter
        self.write("DISPlay:WINDow1:TRACe1:FEED 'CH1_S11'") # BUG: if trace1 already exist, don't change it and controller don't know the error
        self.select_trace()

    def add_s21(self):
        self.set_window_state(True)
        self.write("CALCulate:PARameter:DEFine:EXT 'CH1_S21',S21")  # Define a measurement name, parameter
        self.write("DISPlay:WINDow1:TRACe2:FEED 'CH1_S21'")
        self.select_trace()

    def add_s41(self):
        self.set_window_state(True)
        self.write("CALCulate:PARameter:DEFine:EXT 'CH1_S41',S41")  # Define a measurement name, parameter
        self.write("DISPlay:WINDow1:TRACe3:FEED 'CH1_S41'")
        self.select_trace()

    def delete_trace(self, value):
        value = int(value)
        self.write(f"DISPlay:WINDow1:TRACe{value}:DEL")


    def get_driver_model(self):
        model = []

        model.append({'element':'variable','name':'window_state',
                      'read':self.get_window_state,'write':self.set_window_state,
                      'type':bool,'help':'Activate/deactivate the window 1'})
        model.append({'element':'variable','name':'display',
                      'read':self.get_display,'write':self.set_display,
                      'type':bool,'help':'Display or not the PNA interface (not displaying increase speed communication)'})
        model.append({'element':'variable','name':'select_trace',
                      'read':self.get_trace,'write':self.set_trace,
                      'type':int,'help':'Select a trace by its number'})
        model.append({'element':'action','name':'add_s11',
                      'do':self.add_s11,
                      'help':'Add the S11 trace'})
        model.append({'element':'action','name':'add_s21',
                      'do':self.add_s21,
                      'help':'Add the S21 trace'})
        model.append({'element':'action','name':'add_s41 (electrical)',
                      'do':self.add_s41,
                      'help':'Add the S41 trace'})
        model.append({'element':'action','name':'delete_trace',
                      'do':self.delete_trace,
                      'param_type':int,'help':'Delete the trace'})

        return model


class Markers:

    def __init__(self, dev):

        self.dev = dev
        self.query = dev.query
        self.write = dev.write
        self.opc = dev.opc
        self.wait = dev.wait

        self._bandwidth_target = -3
        self._selected_marker = 1

    def get_marker_state(self):
        return bool(int(float(self.query(f"CALCulate1:MARKer{self._selected_marker}:STATe?"))))

    def set_marker_state(self, value):
        state = int(bool(int(float(value))))
        self.write(f"CALCulate1:MARKer{self._selected_marker}:STATe {state}")


    def get_marker(self):
        return self._selected_marker

    def set_marker(self, value):
        value = int(value)
        self.write(f"CALCulate1:MARKer{value}:STATe ON")
        self._selected_marker = value

    def remove_all_markers(self):
        self.write("CALCulate1:MARKer:AOFF")


    def get_marker_frequency(self):
        self.set_marker_state(True)
        return float(self.query(f"CALCULATE:MARKER{self._selected_marker}:X?"))

    def set_marker_frequency(self, value):
        self.set_marker_state(True)
        value = float(value)
        self.write(f"CALCULATE:MARKER{self._selected_marker}:X {value}")


    def get_marker_y(self):
        self.set_marker_state(True)
        y1, y2 = self.query(f"CALCULATE:MARKER{self._selected_marker}:Y?").split(",")
        y1 = float(y1)
        y2 = float(y2)
        return y1, y2

    def get_marker_power(self):
        return float(self.get_marker_y()[0])

    def get_marker_phase(self):
        return float(self.get_marker_y()[1])



    def search_compression(self):
        value = float(-self._bandwidth_target) # WARNING: set negative value to found the same results as other bandwitdh search
        self.set_marker(5) # anable marker 2
        self.write(f"CALC:MARK5:COMP:LEV {value}") # search compression at given value
        self.wait()
        self.write("CALC:MARK5:FUNC COMPression")  # set function compression to marker 2
        self.wait()
        return float(self.get_marker_frequency()) # markers freq or power I guess


    def get_bandwidth_target(self):
        return float(self._bandwidth_target)

    def set_bandwidth_target(self, value=-3):
        self._bandwidth_target = float(value)


    def search_bandwidth(self): # worked before changes but should NOT use this for EO bandwitdh but ONLY for filter bandwitdh
        """ Search a filter bandwitdh. Bandwitdh is define as interval between left and right markers with max+value power"""
        value = float(self._bandwidth_target)
        # self.remove_all_markers()
        self.opc()
        self.write(f"CALC:MARK:BWID {value}")
        self.write(f"CALC:MARK:BWID {value}")
        self.wait()
        bandwidth, freq_center, Q, loss = self.query("CALCulate:MARKer:BWIDth?").split(",")
        # self.bandwidth_results = float(bandwidth), float(freq_center), float(Q), float(loss)

        return float(bandwidth)

    def search_EO_bandwidth(self):
        sweep_type = str(self.dev.sweep.get_sweep_type())
        assert sweep_type in ("LOG", "LIN"), "Must be a sweep mode, not in a single frequency"

        target = self._bandwidth_target
        low_frequency = float(self.dev.frequency.get_frequency_start())

        self.set_marker(6)
        self.set_marker_frequency(low_frequency)
        self.wait()
        power = float(self.get_marker_power())

        self.set_marker(7)

        self.write(f"CALC:MARK7:TARget {power+target}")
        self.write("CALC:MARK7:FUNC:EXEC TARGET")

        self.wait()
        bandwidth = float(self.get_marker_frequency())

        return bandwidth


    def get_frequency_of_maximum(self):
        self.set_marker(8)
        # self.set_marker_state(True)
        self.write("CALC:MARK8:FUNC:EXEC MAX")
        self.wait()
        return float(self.get_marker_frequency())

    def get_frequency_of_minimum(self):
        self.set_marker(9)
        # self.set_marker_state(True)
        self.write("CALC:MARK9:FUNC:EXEC MIN")
        self.wait()
        return float(self.get_marker_frequency())


    def get_driver_model(self):
        model = []

        model.append({'element':'variable','name':'state',
                      'read':self.get_marker_state,'write':self.set_marker_state,
                      'type':bool,
                      'help':'Activate/deactivate the selected marker'})
        model.append({'element':'variable','name':'select',
                      'read':self.get_marker,'write':self.set_marker,
                      'type':int,
                      'help':'Activate (or select if already exist) the marker with the provided number'})
        model.append({'element':'action','name':'remove_all',
                      'do':self.remove_all_markers,
                      'help':'Remove all markers'})
        model.append({'element':'variable','name':'frequency',
                      'read':self.get_marker_frequency,'write':self.set_marker_frequency,
                      'type':float,'unit':'Hz',
                      'help':'Frequency of the selected marker'})
        model.append({'element':'variable','name':'power',
                      'read':self.get_marker_power,
                      'type':float,'unit':'dBm',
                      'help':'Power (dBm) of the selected marker (or not power if display another param)'})
        model.append({'element':'variable','name':'phase',
                      'read':self.get_marker_phase,
                      'type':float,
                      'help':'Phase of the selected marker (only if measure has two param)'})
        model.append({'element':'variable','name':'bandwidth_target',
                      'read':self.get_bandwidth_target,"write":self.set_bandwidth_target,
                      'type':float,'help':'Set the parameter to -3 to find 3dB bandwitdh'})
        # model.append({'element':'variable','name':'search_bandwidth',
        #               'read':self.search_bandwidth,
        #               'type':float,
        #               'help':'Returns the bandwitdh with the previsouly defined target value'})
        # model.append({'element':'variable','name':'search_EO_bandwidth',
        #               'read':self.search_EO_bandwidth,
        #               'type':float,'unit':'Hz',
        #               'help':'Returns the EO bandwitdh with the previsouly defined target value.\nWarning: find the next target to the right each time the search is done'})
        model.append({'element':'variable','name':'bandwitdh',
                      'read':self.search_compression,
                      'type':float,'unit':'Hz',
                      'help':'Returns the Compression frequency with the previsouly defined target value'})
        model.append({'element':'variable','name':'freq_of_min_power',
                      'read':self.get_frequency_of_minimum,
                      'type':float,'unit':"Hz",
                      'help':'Returns the frequency of the minimum power'})
        model.append({'element':'variable','name':'freq_of_max_power',
                      'read':self.get_frequency_of_maximum,
                      'type':float,'unit':"Hz",
                      'help':'Returns the frequency of the maximum power'})
        return model


class Power:

    def __init__(self, dev):

        self.query = dev.query
        self.write = dev.write


    def get_output_state(self):
        return bool(int(float(self.query("OUTP?"))))

    def set_output_state(self, value):
        state = int(bool(int(float(value))))
        self.write(f"OUTP {state}")


    def get_power(self):
        return float(self.query("SOUR:POW?"))

    def set_power(self, value):
        value = float(value)
        self.write(f"SOUR:POW1 {value}")


    def get_driver_model(self):
        model = []

        model.append({'element':'variable','name':'output',
                      'read':self.get_output_state,'write':self.set_output_state,
                      'type':bool,'help':'Activate/deactivate the output RF power'})
        model.append({'element':'variable','name':'power',
                      'read':self.get_power,'write':self.set_power,
                      'type':float,'unit':'dBm','help':'Set the RF power (dBm)'})
        return model


class Trigger:

    def __init__(self, dev):

        self.query = dev.query
        self.write = dev.write
        self.wait = dev.wait
        self.abort = dev.abort
        self.opc = dev.opc


    def do_single(self):
        self.abort()
        self.set_trigger_continuous(False)
        self.write("SENS:SWE:MODE SINGle")
        self.write("INITIATE:IMMEDIATE")
        self.opc()


    def get_continuous(self):
        ans = self.query("SENSe:SWEep:MODE?")
        ans2 = self.get_trigger_continuous()
        return True if ans == "CONT" and ans2 is True else False

    def set_continuous(self, value):
        value = bool(int(float(value)))

        if value:
            self.write("SENS:SWE:MODE CONTinuous")
        else:
            self.write("SENS:SWE:MODE HOLD")

        self.set_trigger_continuous(value)

        self.opc()


    def get_trigger_continuous(self): # not used but work
        return bool(self.query("INIT:CONT?"))

    def set_trigger_continuous(self, value):
        state = int(bool(int(float(value))))
        self.write(f"INIT:CONT {state}")


    def get_driver_model(self):
        model = []
        model.append({'element':'action','name':'single',
                      'do':self.do_single,
                      'help':'Do a single sweep measurement. IF too long, must change timeout'})

        model.append({'element':'variable','name':'continuous',
                      'read':self.get_continuous,'write':self.set_continuous,
                      'type':bool,'help':'Activate/deactivate continuous sweep measurement TEST'})

        # model.append({'element':'variable','name':'continuous',
        #               'read':self.get_trigger_continuous,'write':self.set_trigger_continuous,
        #               'type':bool,'help':'Activate/deactivate continuous sweep measurement'})
        return model


class Sweep:

    def __init__(self, dev):

        self.query = dev.query
        self.write = dev.write


    def get_sweep_time(self):
        return float(self.query("SENSe1:SWEep:TIME?"))

    def set_sweep_time(self, value):
        value = float(value)
        return self.write(f"SENSe1:SWEep:TIME {value}")


    def get_nbpts(self):
        return int(self.query("SENSe1:SWEep:POINts?"))

    def set_nbpts(self, value):
        value = int(value)
        self.write(f"SENSe1:SWEep:POINts {value}")


    def get_sweep_type(self):
        return str(self.query("SENSe1:SWEep:TYPE?"))

    def set_sweep_type(self, value):
        value = str(value)
        self.write(f"SENSe1:SWEep:TYPE {value}")


    def get_sweep_time_auto(self):
        return bool(int(float(self.query("SENSe1:SWEep:TIME:AUTO?"))))

    def set_sweep_time_auto(self, value):
        state = int(bool(int(float(value))))
        self.write(f"SENSe1:SWEep:TIME:AUTO {state}")


    def set_sweep_analog(self):  # work but don't know what it does
        self.write("SENSe1:SWEep:GENeration ANAL")


    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'sweep_time',
                      'read':self.get_sweep_time,'write':self.set_sweep_time,
                      'type':float,'unit':'s','help':'Set the sweep time (s)'})
        model.append({'element':'variable','name':'points',
                      'read':self.get_nbpts,'write':self.set_nbpts,
                      'type':int,'help':'Set the number of points'})
        model.append({'element':'variable','name':'sweep_type',
                      'read':self.get_sweep_type,'write':self.set_sweep_type,
                      'type':str,'help':'Choose between "LOG" "LIN" and "CW" sweep'})
        model.append({'element':'variable','name':'sweep_time_auto',
                      'read':self.get_sweep_time_auto,'write':self.set_sweep_time_auto,
                      'type':bool,'help':'Activate/deactivate auto sweep time'})

        model.append({'element':'action','name':'sweep_analog',
                      'do':self.set_sweep_analog,
                      'help':'Set analogique sweep'})
        return model


class Frequency:

    def __init__(self, dev):

        self.query = dev.query
        self.write = dev.write


    def get_frequency_start(self):
        return float(self.query("SENS:FREQ:STAR?"))

    def set_frequency_start(self, value):
        value = float(value)
        self.write(f"SENS:FREQ:STAR {value}")


    def get_frequency_stop(self):
        return float(self.query("SENS:FREQ:STOP?"))

    def set_frequency_stop(self, value):
        value = float(value)
        self.write(f"SENS:FREQ:STOP {value}")


    def get_frequency_center(self):
        return float(self.query("SENSe1:FREQuency:CENTer?"))

    def set_frequency_center(self, value):
        value = float(value)
        self.write(f"SENSe1:FREQuency:CENTer {value}")


    def get_frequency_span(self):
        return float(self.query("SENSe1:FREQuency:SPAN?"))

    def set_frequency_span(self, value):
        value = float(value)
        self.write(f"SENSe1:FREQuency:SPAN {value}")


    def get_frequency(self):
        return float(self.query("SENS:FREQ:CW?"))

    def set_frequency(self, value):
        value = float(value)
        self.write(f"SENS:FREQ:CW {value}")


    def get_step(self):
        return float(self.query("SENS:SWEep:STEP?"))

    def set_step(self, value):
        value = float(value)
        self.write(f"SENS:SWEep:STEP {value}")


    def get_driver_model(self):
        model = []

        model.append({'element':'variable','name':'start',
                      'read':self.get_frequency_start,'write':self.set_frequency_start,
                      'type':float,'unit':'Hz','help':'Set the start frequency (Hz)'})

        model.append({'element':'variable','name':'stop',
                      'read':self.get_frequency_stop,'write':self.set_frequency_stop,
                      'type':float,'unit':'Hz','help':'Set the stop frequency (Hz)'})

        model.append({'element':'variable','name':'center',
                      'read':self.get_frequency_center,'write':self.set_frequency_center,
                      'type':float,'unit':'Hz','help':'Set the center frequency (Hz)'})

        model.append({'element':'variable','name':'span',
                      'read':self.get_frequency_span,'write':self.set_frequency_span,
                      'type':float,'unit':'Hz','help':'Set the frequency span (Hz)'})

        model.append({'element':'variable','name':'fixe',
                      'read':self.get_frequency,'write':self.set_frequency,
                      'type':float,'unit':'Hz','help':'Set the CW frequency (Hz)'})

        model.append({'element':'variable','name':'step',
                      'read':self.get_step,'write':self.set_step,
                      'type':float,'unit':'Hz','help':'Set the frequency step (Hz)'})

        return model


class Average:

    def __init__(self, dev):

        self.query = dev.query
        self.write = dev.write


    def do_averaging_restart(self):
        self.write("SENS:AVER:CLE")


    def get_average_count(self):
        return float(self.query("SENSe1:AVERage:Count?"))

    def set_average_count(self, value):
        value = int(value)
        self.write(f"SENSe1:AVERage:Count {value}")


    def get_average_state(self):
        state = bool(int(float(self.query("SENS:AVER?"))))
        return state

    def set_average_state(self, value):
        state = int(bool(int(float(value))))
        self.write(f"SENS:AVER {state}")


    def get_average_type(self):
        ans = self.query("SENS:AVER:MODE?")
        return str(ans)

    def set_average_type(self, value):
        """average sweep if false and average point if true"""
        value = str(value)
        self.write(f"SENS:AVER:MODE {value}")


    def get_smoothing_state(self):
        return bool(int(float(self.query("CALC:SMO?"))))

    def set_smoothing_state(self, value):
        value = int(bool(int(float(value))))
        self.write(f"CALC:SMO {value}")


    def get_smoothing_percent_span(self):
        return float(self.query("CALC:SMO:APER?"))

    def set_smoothing_percent_span(self, value):
        value = float(value)
        self.write(f"CALC:SMO:APER {value}")


    def get_smoothing_points(self):
        return int(self.query("CALC:SMO:POIN?"))

    def set_smoothing_points(self, value):
        value = int(value)
        self.write(f"CALC:SMO:POIN {value}")


    def get_if_bandwitdh(self):
        return float(self.query("SENSe1:BANDwidth?"))

    def set_if_bandwitdh(self, value):
        value = float(value)
        self.write(f"SENSe1:BANDwidth {value}")


    def get_driver_model(self):
        model = []

        model.append({'element':'action','name':'averaging_restart',
                      'do':self.do_averaging_restart,
                      'help':'Restart the averaging process'})

        model.append({'element':'variable','name':'average_count',
                      'read':self.get_average_count,'write':self.set_average_count,
                      'type':int,'help':'Set the averaging count'})
        model.append({'element':'variable','name':'averaging',
                      'read':self.get_average_state,'write':self.set_average_state,
                      'type':bool,'help':'Set the averaging ON/OFF'})
        model.append({'element':'variable','name':'averaging_type',
                      'read':self.get_average_type,'write':self.set_average_type,
                      'type':str,'help':'Select "SWEep" for sweep or "POINt" for average point'})

        model.append({'element':'variable','name':'smoothing',
                      'read':self.get_smoothing_state,'write':self.set_smoothing_state,
                      'type':bool,'help':'Turns data smoothing ON or OFF.'})
        model.append({'element':'variable','name':'smoothing_percent_span',
                      'read':self.get_smoothing_percent_span,'write':self.set_smoothing_percent_span,
                      'type':float,'unit':r'%','help':'Sets the amount of smoothing as a percentage of the number of data points in the channel.'})
        model.append({'element':'variable','name':'smoothing_points',
                      'read':self.get_smoothing_points,'write':self.set_smoothing_points,
                      'type':int,'help':'Sets the number of adjacent data points to average'})

        model.append({'element':'variable','name':'if_bandwitdh',
                      'read':self.get_if_bandwitdh,'write':self.set_if_bandwitdh,
                      'type':float,'unit':'Hz','help':'Set the IF bandwitdh (Hz)'})
        return model



class Data:

    def __init__(self, dev):

        import numpy as np
        self.np = np

        self.query = dev.query
        self.write = dev.write
        self._time_state = True


    def get_data(self):
        data = self.query("CALCulate1:DATA? FDATA").split(",")
        data = [float(i) for i in data]
        return self.np.array(data)

    def save_data_remote(self, filename):  # (save data in "c:\users\public\documents\Network analyzer" by default)
        filename = self.formated_filename(str(filename), ".csv")
        self.create_folder_cascade(filename)
        # "CSV Formatted Data"    "Trace" or "Auto" or "Channel"    "RI" or "MA" or "DB" or "Displayed"    Measurement number
        self.write(f'MMEMory:STORe:DATA "{filename}","CSV Formatted Data","displayed","DB",-1')

    def save_fig(self, filename):
        filename = self.formated_filename(filename, ".png")
        self.create_folder_cascade(filename)
        self.write(f"HCOPy:FILE '{filename}'")


    def get_time_state(self):
        return self._time_state

    def set_time_state(self, value):
        self._time_state = bool(int(float(value)))


    def formated_filename(self, filename, wanted_extension):
        extension = os.path.splitext(filename)[1]

        if extension != wanted_extension:
            filename = filename + wanted_extension

        if self.get_time_state():
            raw_name, extension = os.path.splitext(filename)
            t = time.strftime("%Y%m%d-%H%M%S")
            t = f"_{t}"
            filename = raw_name + t + extension

        return filename


    def load_file(self, filename):
        filename = str(filename)
        self.write(f"MMEM:LOAD '{filename}'")

    def get_default_dir(self):
        return str(self.query("MMEMory:CDIRectory?").strip('"'))
    
    def set_default_dir(self, folder):
        folder= str(folder)
        self.create_folder_cascade(folder)
        self.write(f"MMEMory:CDIRectory '{folder}'")

    def create_folder(self, folder_name):
        folder_name = os.path.join(str(folder_name))
        self.write(f"MMEM:MDIR '{folder_name}'")

            
    def create_folder_cascade(self, filename):
        
        drive = os.path.splitdrive(filename)[0]
 
        ## check if relative or absolute
        if drive == "": # relative path
            default_dir = self.get_default_dir()
            filename = os.path.join(default_dir, filename)
        ##
        
        ## remove filename if given
        path, filename_temp = os.path.split(filename)
        extension = os.path.splitext(filename_temp)[1]
        
        if extension == "":
            fullpath = filename
        else:
            fullpath = path
        ##
        
        drive, path = os.path.splitdrive(fullpath)

        folders = []
        for _ in range(100):  # could use while but don't want to loop if error

            folders.append(os.path.join(drive, path))
            path, folder = os.path.split(path)

            if folder == "" and path != "":
                break

        folders.reverse()

        for folder in folders:
            # if os.path.exists(folder) is False:  # didn't findthe exists version for the PNA
            self.create_folder(folder)


    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'data','unit':'dBm',
                      'read':self.get_data,
                      'type':self.np.ndarray,'help':'Get the power array of the displayed trace (dBm)'})
        model.append({'element':'action','name':'save_data',
                      'do':self.save_data_remote,
                      "param_type":str,'help':'Save a csv file onto the PNA computer containing the frequency, power, phase off all traces'})
        model.append({'element':'action','name':'save_fig',
                      'do':self.save_fig,
                      "param_type":str,'help':'Save the screen image onto the PNA computer (png)'})
        model.append({'element':'variable','name':'add_timestamp',
                      'read':self.get_time_state,'write':self.set_time_state,
                      "type":bool,'help':'Option to add a timestamp to avoid overwriting data'})
        model.append({'element':'action','name':'load_file',
                      'do':self.load_file,
                      "param_type":str,'help':'Load a file from the PNA hard drive.\nCan be state .sta, correction .cal, state and correction .cst, data .sNp with N=1,2,3 or .csa'})
        # model.append({'element':'action','name':'create_folder',
        #               'do':self.create_folder,
        #               "param_type":str,'help':'Create a folder onto the PNA hard drive'})
        model.append({'element':'action','name':'create_folder',
                      'do':self.create_folder_cascade,
                      "param_type":str,'help':'Create all the folders onto the PNA hard drive'})
        model.append({'element':'variable','name':'default_dir',
                      'read':self.get_default_dir, 'write':self.set_default_dir,
                      "type":str,'help':'Change the default path onto the PNA'})
        return model
