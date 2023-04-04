#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified): Yenista CT400.
-
"""

import sys
import os
import ctypes as ct
import xml.etree.ElementTree as ET

import pandas as pd
import numpy as np


# Definition of various constants to use the same names as the C interface
(LS_TunicsPlus, LS_TunicsPurity, LS_TunicsReference, LS_TunicsT100s,
     LS_TunicsT100r, LS_JdsuSws, LS_Agilent, NB_SOURCE) = (0, 1, 2, 3,
                                                           4, 5, 6, 7)
(LI_1, LI_2, LI_3, LI_4) = (1, 2, 3, 4)
(DE_1, DE_2, DE_3, DE_4, DE_5) = (1, 2, 3, 4, 5)
(DISABLE, ENABLE) = (0, 1)
(Unit_mW, Unit_dBm) = (0, 1)

CONNECTION_ERROR = "Error during the connection to the CT400"


def laser_code(name, permute=False):
    code_dict = {
        "TunicsPlus":LS_TunicsPlus,
        "TunicsPurity":LS_TunicsPurity,
        "TunicsReference":LS_TunicsReference,
        "TunicsT100S":LS_TunicsT100s,
        "TunicsT100R":LS_TunicsT100r,
        "JDSU SWS":LS_JdsuSws,
        "Agilent":LS_Agilent,
        "Manual":NB_SOURCE,
        }

    if permute:
        code_dict = dict((new_val,new_k) for new_k,new_val in code_dict.items())

    code = code_dict.get(name)

    if code is None:
        print(f"Didn't recognized the laser name: {name}, took TunicsPlus instead")
        if permute:
            code = "TunicsPlus"
        else:
            code = code_dict["TunicsPlus"]

    return code # {name:code}


def read_xml(file):
    try:
        tree = ET.parse(file)

        common = tree.findall('Configuration/Sources/Common')[0].attrib
        power_scan = float(common["Power"])
        low_wavelength_scan = float(common["Lambda_Min"])
        high_wavelength_scan = float(common["Lambda_Max"])

        res_scan = int(tree.findall('Configuration/Application/Sampling_Step')[0].attrib["Value"])

        address = []
        low_wavelength = []
        high_wavelength = []
        speed = []
        connected = []
        laser_model = []

        sources = tree.findall('Configuration/Sources/Source')
        for source in sources:
            src_att = source.attrib
            # print(src_att)
            address.append(int(src_att["Address"]))
            low_wavelength.append(float(src_att["Lambda_Min"]))
            high_wavelength.append(float(src_att["Lambda_Max"]))
            speed.append(int(src_att["Speed"]))

            connected.append(True if src_att["Enable"] == "True" else False)
            laser_model.append(laser_code(src_att["Type"]))   # doesn't seems to bother execution

        Detector_Array = tree.findall('Configuration/Application/Detector_Array')[0].attrib
        detector_array = []
        for i in (2, 3, 4):  # can add Ext and Orl
            detector_array.append(True if Detector_Array[f"Enable{i}"] == "True" else False)

    except Exception as er:
        print(er, ". Taking default driver value")
        power_scan = 1.
        low_wavelength_scan = 1510.
        high_wavelength_scan = 1610.
        res_scan = 5

        address = [12, 13, 14, 15]
        low_wavelength = [1510., 1310., 1600., 1700.]
        high_wavelength = [1610., 1400., 1700., 1800.]
        speed = [100, 50, 100, 20]

        connected = [ENABLE, DISABLE, DISABLE, DISABLE]
        laser_model = [LS_TunicsPlus, LS_TunicsT100s, LS_TunicsPlus, LS_TunicsPlus]

        detector_array = [DISABLE, DISABLE, DISABLE]

    config = {
        "address": address,
        "low_wavelength": low_wavelength,
        "high_wavelength": high_wavelength,
        "speed": speed,
        "connected": connected,
        "laser_model": laser_model,
        "power_scan": power_scan,
        "low_wavelength_scan": low_wavelength_scan,
        "high_wavelength_scan": high_wavelength_scan,
        "res_scan": res_scan,
        "detector_array":detector_array}
    return config


def default_xml():
    import xml.etree.ElementTree as ET

    # create the default file structure
    CT400 = ET.Element('CT400')
    About = ET.SubElement(CT400, 'About')
    Release = ET.SubElement(About, 'Release')
    Release.set('Value', 'v 3.7.4')
    CT400_Type = ET.SubElement(About, 'CT400_Type')
    CT400_Type.set('Value', '- - - - - -')
    Source = ET.SubElement(About, 'Source')

    TLS1 = ET.SubElement(Source, 'TLS')
    TLS1.set('Name', '1')
    TLS1.set('Available','- - - - - -')
    TLS2 = ET.SubElement(Source, 'TLS')
    TLS2.set('Name', '2')
    TLS2.set('Available', '- - - - - -')
    TLS3 = ET.SubElement(Source, 'TLS')
    TLS3.set('Name', '3')
    TLS3.set('Available', '- - - - - -')
    TLS4 = ET.SubElement(Source, 'TLS')
    TLS4.set('Name', '4')
    TLS4.set('Available', '- - - - - -')

    Detector_Array = ET.SubElement(About, 'Detector_Array')
    Detector_Array.set('TLS1', '- - - - - -')
    Detector_Array.set('TLS2', '- - - - - -')
    Detector_Array.set('TLS3', '- - - - - -')
    Detector_Array.set('TLS4', '- - - - - -')
    Configuration = ET.SubElement(CT400, 'Configuration')
    Sources = ET.SubElement(Configuration, 'Sources')

    Common = ET.SubElement(Sources, 'Common')
    Common.set('Power', '3.000000')
    Common.set('Lambda_Min', '1551.000000')
    Common.set('Lambda_Max', '1560.000000')

    Source1 = ET.SubElement(Sources, 'Source')
    Source1.set('Name', 'TLS_0')
    Source1.set('Enable', 'True')
    Source1.set('Address', '12')
    Source1.set('Lambda_Min', '1510.000000')
    Source1.set('Lambda_Max', '1590.000000')
    Source1.set('Speed', '100')
    Source1.set('Type', 'TunicsPlus')

    Source2 = ET.SubElement(Sources, 'Source')
    Source2.set('Name', 'TLS_1')
    Source2.set('Enable', 'False')
    Source2.set('Address', '9')
    Source2.set('Lambda_Min', '1350.000000')
    Source2.set('Lambda_Max', '1510.000000')
    Source2.set('Speed', '100')
    Source2.set('Type', 'TunicsT100S')

    Source3 = ET.SubElement(Sources, 'Source')
    Source3.set('Name', 'TLS_2')
    Source3.set('Enable', 'False')
    Source3.set('Address', '12')
    Source3.set('Lambda_Min', '1500.000000')
    Source3.set('Lambda_Max', '1680.000000')
    Source3.set('Speed', '100')
    Source3.set('Type', 'TunicsT100S')

    Source4 = ET.SubElement(Sources, 'Source')  # True default values for unknown laser (take CT400 min max values and tell variable name to use for communication)
    Source4.set('Name', 'TLS_3')
    Source4.set('Enable', 'False')
    Source4.set('Address', '1')
    Source4.set('Lambda_Min', '1250.000000')
    Source4.set('Lambda_Max', '1650.000000')
    Source4.set('Speed', '100')
    Source4.set('Type', 'Manual')

    Source4.set('Power_On', 'Enable')
    Source4.set('Power_Off', 'Disable')
    Source4.set('Power', 'P=%2.3f')
    Source4.set('WaveLength', 'L=%4.3f')
    Source4.set('CmdSpeed', 'MOTOR_SPEED=%d')

    Application = ET.SubElement(Configuration, 'Application')
    Cursor = ET.SubElement(Application, 'Cursor')
    Cursor.set('Visible', 'True')
    Cursor.set('Cursor', 'True')
    Cursor.set('Marker', 'False')
    Sampling_Step = ET.SubElement(Application, 'Sampling_Step')
    Sampling_Step.set('Value', '1')
    Trigger = ET.SubElement(Application, 'Trigger')
    Trigger.set('Value', 'False')
    External_Synchronization = ET.SubElement(Application, 'External_Synchronization')
    External_Synchronization.set('Value', 'False')
    Detector_Array = ET.SubElement(Application, 'Detector_Array')
    Detector_Array.set('Enable2', 'False')
    Detector_Array.set('Enable3', 'False')
    Detector_Array.set('Enable4', 'False')
    Detector_Array.set('EnableExt', 'False')
    Detector_Array.set('EnableOrl', 'False')
    BNC_Input = ET.SubElement(Application, 'BNC_Input')
    BNC_Input.set('Enable', 'False')
    BNC_Input.set('Alpha', '0.000000E+00')
    BNC_Input.set('Beta', '0.000000E+00')
    BNC_Input.set('Unit', 'mW')
    Measurement = ET.SubElement(Application, 'Measurement')
    Measurement.set('Type', 'Single')
    Measurement.set('Is_Scan_Max_Used', 'False')
    Measurement.set('Scan_Number', '1')
    Measurement.set('Reset_Min_Max', 'False')
    Measurement.set('Reset_Modulo', '2')
    Measurement.set('Scan_Delay', '1')
    Measurement.set('Is_Scan_Save', 'True')
    Measurement.set('Continuous_Scan_Files_Directory', r'C:\Users\Public\Documents\Yenista Optics\CT400\Data')
    Measurement.set('File_Type', 'TXT')
    Measurement.set('KeepModeHope', 'False')
    MeasurementDisplay = ET.SubElement(Application, 'MeasurementDisplay')
    MeasurementDisplay.set('FWHM_Threshold', '-35.000000')
    MeasurementDisplay.set('FWHM_Power', '-3.000000')
    MeasurementDisplay.set('SideFrontTopPower', '-3.000000')
    MeasurementDisplay.set('SideFrontBottomPower', '-40.000000')
    MeasurementDisplay.set('Show_Info', 'False')
    Zoom = ET.SubElement(Application, 'Zoom')
    Zoom.set('Status', 'WaveLength')
    Passband = ET.SubElement(Configuration, 'Passband')
    Passband_Configuration = ET.SubElement(Passband, 'Configuration')
    Passband_Configuration.set('Threshold', '-30.000000')
    Passband_Configuration.set('Grid', '0')
    Passband_Configuration.set('Bandwidth1', '-1.000000')
    Passband_Configuration.set('Bandwidth2', '-3.000000')
    Passband_Configuration.set('Bandwidth3', '-20.000000')
    Passband_Configuration.set('OWR', '10.000000')
    Alarms = ET.SubElement(Passband, 'Alarms')
    Alarms.set('ChannelCentration', '20.000000')
    Alarms.set('minBandwidth1', '1.000000')
    Alarms.set('maxBandwidth1', '1.000000')
    Alarms.set('minBandwidth2', '1.000000')
    Alarms.set('maxBandwidth2', '1.000000')
    Alarms.set('minBandwidth3', '1.000000')
    Alarms.set('maxBandwidth3', '1.000000')
    Alarms.set('maxIL', '5.000000')
    Alarms.set('ripple', '0.500000')
    Alarms.set('adjacent', '40.000000')
    Alarms.set('noAdjacent', '50.000000')

    return CT400

def write_xml(config, configpath):
    try:
        import xml.etree.ElementTree as ET
        from xml.dom import minidom

        # open existing or create default file structure
        if os.path.exists(configpath):
            CT400_tree = ET.parse(configpath)
            CT400 = CT400_tree.getroot()
            try:
                import shutil
                shutil.copyfile(configpath, configpath+".backup")
            except:
                pass
        else:
            CT400 = default_xml()

        # modify the file structure values using config (not all variables are included in config)
        Common = CT400.findall('Configuration/Sources/Common')[0]
        Sampling_Step = CT400.findall('Configuration/Application/Sampling_Step')[0]
        sources = CT400.findall('Configuration/Sources/Source')

        Common.set('Power', "%.6f" % (config["power_scan"]))
        Common.set('Lambda_Min', "%.6f" % (config["low_wavelength_scan"]))
        Common.set('Lambda_Max', "%.6f" % (config["high_wavelength_scan"]))
        Sampling_Step.set('Value', "%i" % (config["res_scan"]))

        for i, source in enumerate(sources):
            try:
                source.set('Address', "%i" % (config["address"][i]))
                source.set('Enable', str(config["connected"][i]))
                source.set('Lambda_Min', "%.6f" % (config["low_wavelength"][i]))
                source.set('Lambda_Max', "%.6f" % (config["high_wavelength"][i]))
                source.set('Speed', "%i" % (config["speed"][i]))
                source.set('Type', str(laser_code(config["laser_model"][i], permute=True)))
            except IndexError:
                pass
        Detector_Array = CT400.findall('Configuration/Application/Detector_Array')[0]
        for ind, i in enumerate((2, 3, 4)):  # can add Ext and Orl
        # TODO: same try expect here if no detector ?
            Detector_Array.set(f"Enable{i}", str(config["detector_array"][ind]))


        # create and format xml file
        dom = minidom.parseString(ET.tostring(CT400))
        mydata_pretty = dom.toprettyxml(indent='\t')
        mydata_pretty = mydata_pretty.split('<?xml version="1.0" ?>\n')[1]
        mydata_pretty = mydata_pretty.replace("/>", " />")
        data_list = [string.rstrip() for string in mydata_pretty.split("\n")]
        data_list = list(filter(None, data_list))
        mydata_pretty = "\n".join(data_list)

        # write xml file
        # configpath = os.path.splitext(configpath)[0]+"_2"+os.path.splitext(configpath)[1]
        with open(configpath, "w") as f:
            f.write(mydata_pretty)

    except FileNotFoundError:
        pass

# config = read_xml(r'C:\Users\Public\Documents\Yenista Optics\CT400\Config\CT400.config.xml')
# write_xml(config, r'C:\Users\Public\Documents\Yenista Optics\CT400\Config\CT400.config.xml')
# %%

class Laser:
    """ Contain all the ct400 commands related to the laser"""

    def __init__(self, dev, num=LI_1):  # dev is the detector instance
        self.dev = dev
        self.config = self.dev.dev.config
        self.NUM = num
        self._init_variables()

        try:
            self.connect()
        except Exception as er:
            print(f"laser{self.NUM}:", er)

    def connect(self):
        try:
            self.controller = self.dev.controller
        except Exception:
            raise FileNotFoundError("Can't found the CT400")

        self.uiHandle = self.dev.uiHandle

        try:
            self._init_laser()
        except Exception:
            raise FileNotFoundError("Can't found the laser")

    def _init_variables(self):
        self._address = self.config["address"][self.NUM-1]
        self._laser_model = self.config["laser_model"][self.NUM-1]
        self._connected = self.config["connected"][self.NUM-1]
        self._low_wavelength = self.config["low_wavelength"][self.NUM-1]
        self._high_wavelength = self.config["high_wavelength"][self.NUM-1]
        self._speed = self.config["speed"][self.NUM-1]

        self._state = False
        self._power = 1.
        self._wavelength = 1550.

    def _init_laser(self):
        self.controller.CT400_SetLaser(self.uiHandle, self.NUM, self._connected, self._address,
                             self._laser_model,
                             ct.c_double(self._low_wavelength),
                             ct.c_double(self._high_wavelength),
                             self._speed)


    def get_model(self):
        return self._laser_model

    def set_model(self, value):
        self._laser_model = int(value)
        self._init_laser()


    def get_address(self):
        return self._address

    def set_address(self, value):
        self._address = int(value)
        self._init_laser()


    def get_low_wavelength(self):
        return self._low_wavelength

    def set_low_wavelength(self, value):
        self._low_wavelength = float(value)
        self._init_laser()


    def get_high_wavelength(self):
        return self._high_wavelength

    def set_high_wavelength(self, value):
        self._high_wavelength = float(value)
        self._init_laser()


    def get_speed(self):
        return self._speed

    def set_speed(self, value):
        self._speed = int(value)
        self.controller.CT400_SetSamplingResolution(self.uiHandle, self._speed)


    def get_connected(self):
        return self._connected

    def set_connected(self, value):
        self._connected = bool(int(float(value)))
        self._init_laser()


    def get_output_state(self):
        return self._state

    def set_output_state(self, state):
        self._state = ENABLE if bool(int(float(state))) else DISABLE
        self.controller.CT400_CmdLaser(self.uiHandle, self.NUM, self._state,
                             ct.c_double(self._wavelength), ct.c_double(self._power))


    def get_wavelength(self):
        return self._wavelength

    def set_wavelength(self, value):
        self._wavelength = float(value)
        self.controller.CT400_CmdLaser(self.uiHandle, self.NUM, self._state,
                             ct.c_double(self._wavelength), ct.c_double(self._power))


    def get_power(self):
        return self._power

    def set_power(self, value):
        self._power = float(value)
        self.controller.CT400_CmdLaser(self.uiHandle, self.NUM, self._state,
                             ct.c_double(self._wavelength), ct.c_double(self._power))


    def get_driver_model(self):
        config = []

        config.append({'element':'variable','name':'output','type':bool,
                       'read':self.get_output_state, 'write':self.set_output_state,
                       "help": "Turn on/off the laser using boolean"})

        config.append({'element':'variable','name':'wavelength','unit':'nm','type':float,
                       'read':self.get_wavelength,'write':self.set_wavelength,
                       "help": "Set the laser wavelength in nm"})

        config.append({'element':'variable','name':'power','unit':'mW','type':float,
                       'read':self.get_power,'write':self.set_power,
                       'help':'Set the laser output power in mW'})

        config.append({'element':'variable','name':'low_wavelength','unit':'nm','type':float,
                       'read':self.get_low_wavelength,'write':self.set_low_wavelength,
                       'help':'Set the starting wavelength of this laser for the scan in nm'})

        config.append({'element':'variable','name':'high_wavelength','unit':'nm','type':float,
                       'read':self.get_high_wavelength,'write':self.set_high_wavelength,
                       'help':'Set the end wavelength of this laser for the scan in nm'})

        config.append({'element':'variable','name':'speed','unit':'nm/s','type':int,
                       'read':self.get_speed,'write':self.set_speed,
                       'help':'Set the laser wavelength scan speed in nm/s'})

        # config.append({'element':'action','name':'connect_laser','do':self.connect,
        #                "help": "Try to connect to the laser"})

        config.append({'element':'variable','name':'laser_address','type':int,
                       'read':self.get_address,'write':self.set_address,
                       "help": "Set the laser address"})

        config.append({'element':'variable','name':'laser_model','type':int,
                       'read':self.get_model,'write':self.set_model,
                       "help": "Set the laser model \n(LS_TunicsPlus, LS_TunicsPurity, LS_TunicsReference, LS_TunicsT100s, LS_TunicsT100r, LS_JdsuSws, LS_Agilent, NB_SOURCE) \n(0, 1, 2, 3, 4, 5, 6, 7)"})

        config.append({'element':'variable','name':'connected','type':bool,
                       'read':self.get_connected, 'write':self.set_connected,
                       "help": "Boolean for connected laser"})
        return config


class Scan:
    """ Contain all the ct400 commands related to the laser"""

    def __init__(self, dev):  # dev is the detector instance
        self.dev = dev
        self.config = self.dev.dev.config
        self._init_variables()

        self._interpolate = False

        self.tcError = ct.create_string_buffer(1024)

        try:
            self.connect()
        except Exception as er:
            print("Scan: ", er)

    def connect(self):
        try:
            self.controller = self.dev.controller
        except Exception:
            raise FileNotFoundError("Can't found the CT400")

        self.uiHandle = self.dev.uiHandle

        try:
            self._init_scan()
        except Exception:
            raise FileNotFoundError("Can't found any laser")


    def _init_variables(self):
        self._power_scan = self.config['power_scan']
        self._low_wavelength_scan = self.config["low_wavelength_scan"]
        self._high_wavelength_scan = self.config["high_wavelength_scan"]
        self._res = self.config["res_scan"]
        for ind, i in enumerate((2, 3, 4)):  # can add Ext and Orl
            setattr(self, f"_detector{i}_state", self.config["detector_array"][ind])
        self._input_source = 1

    def _init_scan(self):
        self.set_scan(self._power_scan, self._low_wavelength_scan, self._high_wavelength_scan)
        self.set_res(self._res)


    def get_low_wavelength_scan(self):
        return self._low_wavelength_scan

    def set_low_wavelength_scan(self, value):
        self._low_wavelength_scan = float(value)
        self.set_scan(self._power_scan, self._low_wavelength_scan, self._high_wavelength_scan)


    def get_high_wavelength_scan(self):
        return self._high_wavelength_scan

    def set_high_wavelength_scan(self, value):
        self._high_wavelength_scan = float(value)
        self.set_scan(self._power_scan, self._low_wavelength_scan, self._high_wavelength_scan)


    def set_scan(self, power, low_wl, high_wl):
        self.controller.CT400_SetScan(
                self.uiHandle,
                ct.c_double(power),
                ct.c_double(low_wl),
                ct.c_double(high_wl))


    def get_res(self):
        return self._res

    def set_res(self, value):
        self._res = int(value)
        self.controller.CT400_SetSamplingResolution(self.uiHandle, self._res)


    def get_interpolate(self):
        return self._interpolate

    def set_interpolate(self, value):
        self._interpolate = bool(int(float(value)))


    def get_power_scan(self):
        return self._power_scan

    def set_power_scan(self, value):
        self._power_scan = float(value)
        self.set_scan(self._power_scan, self._low_wavelength_scan, self._high_wavelength_scan)


    def get_detector2_state(self):
        return self._detector2_state

    def set_detector2_state(self, value):
        self._detector2_state = bool(int(float(value)))

    def get_detector3_state(self):
        return self._detector3_state

    def set_detector3_state(self, value):
        self._detector3_state = bool(int(float(value)))

    def get_detector4_state(self):
        return self._detector4_state

    def set_detector4_state(self, value):
        self._detector4_state = bool(int(float(value)))


    def do_sweep(self):
        for i in range(1,4+1):
            laser = getattr(self.dev.dev, f"laser{i}", None)
            if laser is not None and laser._connected:
                laser._state = ENABLE

        self.controller.CT400_SetDetectorArray(self.uiHandle,
                                               self._detector2_state,
                                               self._detector3_state,
                                               self._detector4_state,
                                               DISABLE)  # eExt

        self.controller.CT400_SetBNC(self.uiHandle, DISABLE, ct.c_double(0.0), ct.c_double(0.0), Unit_mW)

        self.set_scan(self._power_scan, self._low_wavelength_scan, self._high_wavelength_scan)

        self.controller.CT400_ScanStart(self.uiHandle)
        iErrorID = self.controller.CT400_ScanWaitEnd(self.uiHandle, self.tcError)

        assert iErrorID == 0, 'Error during sweep: '+repr(self.tcError.value)[2:-1]


        self._get_data_sweep()


    def _get_data_sweep(self):
        if self._interpolate:
            iPointsNumberResampled = self.controller.CT400_GetNbDataPointsResampled(self.uiHandle)
            DataArraySizeResampled = ct.c_double * iPointsNumberResampled
            (dWavelengthResampled, dPowerResampled, dDetector1Resampled) = (DataArraySizeResampled(), DataArraySizeResampled(), DataArraySizeResampled())
            self.controller.CT400_ScanGetWavelengthResampledArray(self.uiHandle, ct.byref(dWavelengthResampled), iPointsNumberResampled)
            self.controller.CT400_ScanGetPowerResampledArray(self.uiHandle, ct.byref(dPowerResampled), iPointsNumberResampled)
            self.controller.CT400_ScanGetDetectorResampledArray(self.uiHandle, DE_1, ct.byref(dDetector1Resampled), iPointsNumberResampled)

            results_interp = {"L": np.array(dWavelengthResampled, dtype=float),
                              "O": np.array(dPowerResampled, dtype=float),
                              "1": np.array(dDetector1Resampled, dtype=float)}

            if self._detector2_state:
                dDetector2Resampled = DataArraySizeResampled()
                self.controller.CT400_ScanGetDetectorResampledArray(self.uiHandle, DE_2, ct.byref(dDetector2Resampled), iPointsNumberResampled)
                results_interp["2"] = np.array(dDetector2Resampled, dtype=float)

            if self._detector3_state:
                dDetector3Resampled = DataArraySizeResampled()
                self.controller.CT400_ScanGetDetectorResampledArray(self.uiHandle, DE_3, ct.byref(dDetector3Resampled), iPointsNumberResampled)
                results_interp["3"] = np.array(dDetector3Resampled, dtype=float)

            if self._detector4_state:
                dDetector4Resampled = DataArraySizeResampled()
                self.controller.CT400_ScanGetDetectorResampledArray(self.uiHandle, DE_4, ct.byref(dDetector4Resampled), iPointsNumberResampled)
                results_interp["4"] = np.array(dDetector4Resampled, dtype=float)

            results = results_interp

        else:
            iPointsNumber = self.controller.CT400_GetNbDataPoints(self.uiHandle)
            DataArraySize = ct.c_double * iPointsNumber
            (dWavelengthSync, dPowerSync, dDetector1Sync) = (DataArraySize(), DataArraySize(), DataArraySize())
            self.controller.CT400_ScanGetWavelengthSyncArray(self.uiHandle, ct.byref(dWavelengthSync), iPointsNumber)
            self.controller.CT400_ScanGetPowerSyncArray(self.uiHandle, ct.byref(dPowerSync), iPointsNumber)
            self.controller.CT400_ScanGetDetectorArray(self.uiHandle, DE_1, ct.byref(dDetector1Sync), iPointsNumber)

            results_raw = {"L": np.array(dWavelengthSync, dtype=float),
                           "O": np.array(dPowerSync, dtype=float),
                           "1": np.array(dDetector1Sync, dtype=float),
                           }

            if self._detector2_state:
                dDetector2Sync = DataArraySize()
                self.controller.CT400_ScanGetDetectorArray(self.uiHandle, DE_2, ct.byref(dDetector2Sync), iPointsNumber)
                results_raw["2"] = np.array(dDetector2Sync, dtype=float)

            if self._detector3_state:
                dDetector3Sync = DataArraySize()
                self.controller.CT400_ScanGetDetectorArray(self.uiHandle, DE_3, ct.byref(dDetector3Sync), iPointsNumber)
                results_raw["3"] = np.array(dDetector3Sync, dtype=float)

            if self._detector4_state:
                dDetector4Sync = DataArraySize()
                self.controller.CT400_ScanGetDetectorArray(self.uiHandle, DE_4, ct.byref(dDetector4Sync), iPointsNumber)
                results_raw["4"] = np.array(dDetector4Sync, dtype=float)

            results = results_raw

        # dWavelengthSync = np.linspace(1510.2, 1610, 1001)  # used to test without the ct400
        # dPowerSync = np.random.random(dWavelengthSync.shape)
        # dDetector1Sync = np.random.random(dWavelengthSync.shape)

        # dWavelengthResampled = np.linspace(1510, 1610, 1001)  # used to test without the ct400
        # dPowerResampled = dPowerSync
        # dDetector1Resampled = dDetector1Sync

        data = {"Last Scan": pd.DataFrame(results)}

        self.dev.dev.data.update(data)
        self.dev.dev._last_data_name = "Last Scan"


    def get_data(self):
        return pd.DataFrame(self.dev.dev.data.get("Last Scan"))  # better to let Last Scan to avoid saving data from loaded data
        # return pd.DataFrame(self.dev.dev.data.get(self.dev.dev._last_data_name))


    def get_input_source(self):
        return self._input_source

    def set_input_source(self, value):
        assert value in (1,2,3,4), f"Laser number could be 1,2,3,4 not {value}"
        self._input_source = int(value)  # OPTIMIZE: could only take available source using self.detectors._NBR_INPUT
        self.controller.CT400_SwitchInput(self.uiHandle, self._input_source)  # BUG: doesn't work for me


    def get_driver_model(self):
        config = []

        config.append({'element':'variable','name':'power','unit':'mW','type':float,
                       'read':self.get_power_scan,'write':self.set_power_scan,
                       'help':'Set the lasers output power in mW for the scan'})

        config.append({'element':'variable','name':'low_wavelength','unit':'nm','type':float,
                       'read':self.get_low_wavelength_scan,'write':self.set_low_wavelength_scan,
                       'help':'Set the starting wavelength of the scan in nm'})

        config.append({'element':'variable','name':'high_wavelength','unit':'nm','type':float,
                       'read':self.get_high_wavelength_scan,'write':self.set_high_wavelength_scan,
                       'help':'Set the end wavelength of the scan in nm'})

        config.append({'element':'variable','name':'resolution','unit':'pm','type':int,
                       'read':self.get_res,'write':self.set_res,
                       'help':'Set the wavelength resolution of the scan in pm'})

        config.append({'element':'action','name':'sweep','do':self.do_sweep,
                       'help':'Start the scan'})

        config.append({'element':'variable','name':'data','type':pd.DataFrame,
                       'read':self.get_data,
                       "help": "Return the data stored"})

        config.append({'element':'variable','name':'interpolate','type':bool,
                       'read':self.get_interpolate,'write':self.set_interpolate,
                       'help':'Set if want interpolated or raw scan data'})

        config.append({'element':'variable','name':'detector2','type':bool,
                       'read':self.get_detector2_state,'write':self.set_detector2_state,
                       'help':'Set if detector 2 is measured in scan'})

        config.append({'element':'variable','name':'detector3','type':bool,
                       'read':self.get_detector3_state,'write':self.set_detector3_state,
                       'help':'Set if detector 3 is measured in scan'})

        config.append({'element':'variable','name':'detector4','type':bool,
                       'read':self.get_detector4_state,'write':self.set_detector4_state,
                       'help':'Set if detector 4 is measured in scan'})

        config.append({'element':'variable','name':'input_source','type':int,
                       'read':self.get_input_source,'write':self.set_input_source,
                       'help':'Select the input source laser (1,2,3,4)'})

        return config


class Detectors:
    """ Contain only the ct400 commands related to the detectors (no laser commands)"""

    def __init__(self, dev, libpath):
        self.libpath = libpath

        self.dev = dev  # used by the laser

        try:
            self.connect()
        except Exception as er:
            print("Detectors: ", er)

    def connect(self):
        try:
            ct.windll.LoadLibrary(os.path.join(os.path.dirname(self.libpath), "SiUSBXp.dll"))
            self.controller = ct.windll.LoadLibrary(self.libpath)
        except OSError:
            raise OSError("Can't found the CT400")


        uiHandle = ct.c_longlong(self.controller.CT400_Init())

        assert uiHandle != 0, CONNECTION_ERROR

        self.uiHandle = uiHandle
        self._NBR_INPUT = self.controller.CT400_GetNbInputs(self.uiHandle)
        self._NBR_DETECTOR = self.controller.CT400_GetNbDetectors(self.uiHandle)
        self._OPTION = self.controller.CT400_GetCT400Type(self.uiHandle)

        assert self.controller.CT400_CheckConnected(self.uiHandle), CONNECTION_ERROR


    def get_spectral_lines(self):
        iLinesDetected = self.controller.CT400_GetNbLinesDetected(self.uiHandle)
        LinesArraySize = ct.c_double * iLinesDetected
        dLinesValues = LinesArraySize()
        self.controller.CT400_ScanGetLinesDetectionArray(self.uiHandle, ct.byref(dLinesValues) ,iLinesDetected)
        return dLinesValues


    def get_detector_power(self):
        PowerArraySize = ct.c_double * 1
        (Pout, P1, P2, P3, P4, Vext) = (PowerArraySize(), PowerArraySize(), PowerArraySize(), PowerArraySize(), PowerArraySize(), PowerArraySize())
        self.controller.CT400_ReadPowerDetectors(self.uiHandle, ct.byref(Pout), ct.byref(P1), ct.byref(P2), ct.byref(P3), ct.byref(P4), ct.byref(Vext))
        (Pout, P1, P2, P3, P4, Vext) = (float(Pout[0]), float(P1[0]), float(P2[0]), float(P3[0]), float(P4[0]), float(Vext[0]))
        (Pout, P1, P2, P3, P4, Vext) = (round(Pout, 3), round(P1, 3), round(P2, 3), round(P3, 3), round(P4, 3), round(Vext, 3))
        return Pout, P1, P2, P3, P4, Vext

    def get_detector_power0(self):
        return self.get_detector_power()[0]

    def get_detector_power1(self):
        return self.get_detector_power()[1]

    def get_detector_power2(self):
        return self.get_detector_power()[2]

    def get_detector_power3(self):
        return self.get_detector_power()[3]

    def get_detector_power4(self):
        return self.get_detector_power()[4]

    def get_vext(self):
        return self.get_detector_power()[5]

    def get_driver_model(self):
        config = []

        config.append({'element':'variable','name':'Pout','unit':'dBm','type':float,
                        'read':self.get_detector_power0,'help':'Power out CT400 in dBm'})

        config.append({'element':'variable','name':'P_detector1','unit':'dBm','type':float,
                        'read':self.get_detector_power1,'help':'Power in detector 1 in dBm'})

        config.append({'element':'variable','name':'P_detector2','unit':'dBm','type':float,
                        'read':self.get_detector_power2,'help':'Power in detector 2 in dBm'})

        config.append({'element':'variable','name':'P_detector3','unit':'dBm','type':float,
                        'read':self.get_detector_power3,'help':'Power in detector 3 in dBm'})

        config.append({'element':'variable','name':'P_detector4','unit':'dBm','type':float,
                        'read':self.get_detector_power4,'help':'Power in detector 4 in dBm'})

        config.append({'element':'variable','name':'Vext','unit':'V','type':float,
                        'read':self.get_vext,'help':'Voltage ext in V'})

        # config.append({'element':'action','name':'connect_ct400','do':self.connect, "help": "Try to connect the ct400"})
        return config


    def close(self):
        #print("removed close func due to error") # BUG: find it, if add 4 laser but only contain 3, error when closing ct400. Need to only add the correct number of laser (use variable nbr_laser)
        self.controller.CT400_Close(self.uiHandle)



class Driver():

    def __init__(self, libpath, configpath):

        self.libpath = libpath
        self.configpath = configpath

        self.config = read_xml(configpath)

        self.data = dict()
        self._last_data_name = ""

        sys.path.append(os.path.dirname(__file__))
        from interface import Interface

        self.interface = Interface(self)

        self.detectors = Detectors(self, self.libpath)

        if not hasattr(self.detectors, "_NBR_INPUT"):
            self.detectors._NBR_INPUT = 4

        self.nl = self.detectors._NBR_INPUT
        for i in range(1,self.nl+1):
            setattr(self,f'laser{i}',Laser(self.detectors,i))

        self.scan = Scan(self.detectors)


    def available_data(self):
        return list(self.data.keys())

    def disp_available_data(self):
        return str(self.available_data())

    def get_config(self):
        config = {
            "address": [getattr(self, f"laser{i}")._address for i in range(1, self.nl+1)],
            "low_wavelength": [getattr(self, f"laser{i}")._low_wavelength for i in range(1, self.nl+1)],
            "high_wavelength": [getattr(self, f"laser{i}")._high_wavelength for i in range(1, self.nl+1)],
            "speed":[getattr(self, f"laser{i}")._speed for i in range(1, self.nl+1)],
            "connected": [getattr(self, f"laser{i}")._connected for i in range(1, self.nl+1)],
            "laser_model": [getattr(self, f"laser{i}")._laser_model for i in range(1, self.nl+1)],
            "power_scan": self.scan._power_scan,
            "low_wavelength_scan": self.scan._low_wavelength_scan,
            "high_wavelength_scan": self.scan._high_wavelength_scan,
            "res_scan": self.scan._res,
            "detector_array": [getattr(self.scan, f"_detector{i}_state") for i in (2, 3, 4)]
            }
        return config

    def get_driver_model(self):

        config = []

        interface = self.__dict__.get("interface")
        if interface is not None:
            config.append({'element':'module','name':'interface','object':getattr(self,'interface')})

        config.append({'element':'module','name':'detectors','object':getattr(self,'detectors')})
        config.append({'element':'variable','name':'available_data','read':self.disp_available_data,'type':str})
        for i in range(1,self.nl+1):
            config.append({'element':'module','name':f'laser{i}','object':getattr(self,f'laser{i}')})

        config.append({'element':'module','name':'scan','object':getattr(self,'scan')})

        return config


#################################################################################
############################## Connections classes ##############################
class Driver_DLL(Driver):
    def __init__(self,
        libpath=r"C:\Program Files (x86)\Yenista Optics\CT400\Library 1.3.2\Win64\CT400_lib.dll",
        configpath=r'C:\Users\Public\Documents\Yenista Optics\CT400\Config\CT400.config.xml',
        **kwargs):

        self.ct400_command_list = [
            "CT400_Init",
            "CT400_CheckConnected",
            "CT400_GetNbInputs",
            "CT400_GetNbDetectors",
            "CT400_GetCT400Type",
            "CT400_SetLaser",
            "CT400_CmdLaser",
            "CT400_SetScan",
            "CT400_SetSamplingResolution",
            "CT400_SetDetectorArray",
            "CT400_SetBNC",
            "CT400_ScanStart",
            "CT400_ScanWaitEnd",
            "CT400_GetNbDataPoints",
            "CT400_ScanGetWavelengthSyncArray",
            "CT400_ScanGetPowerSyncArray",
            "CT400_ScanGetDetectorArray",
            "CT400_GetNbDataPointsResampled",
            "CT400_ScanGetWavelengthResampledArray",
            "CT400_ScanGetPowerResampledArray",
            "CT400_ScanGetDetectorResampledArray",
            "CT400_ScanSaveWavelengthSyncFile",
            "CT400_ScanSavePowerSyncFile",
            "CT400_ScanSaveDetectorFile",
            "CT400_ScanSaveWavelengthResampledFile",
            "CT400_ScanSavePowerResampledFile",
            "CT400_ScanSaveDetectorResampledFile",
            ## not used ##
            "CT400_SwitchInput",  # may need that if use diff laser
            "CT400_ResetCalibration",
            "CT400_UpdateCalibration",
            "CT400_SetExternalSynchronizationIN",
            "CT400_SetExternalSynchronization",
            "ScanGetLineDetectionArray",
            ## see CT400_PG.pdf for all commands and explainations
            ]

        Driver.__init__(self, libpath, configpath)


    def close(self):
        try:
            self.detectors.close()
        except Exception as er:
            print("Warning, CT400 didn't close properly:", er)
        try:
            self.config = self.get_config()
            write_xml(self.config, self.configpath)
        except Exception as er:
            print("Warning, CT400 config file not saved:", er)
############################## Connections classes ##############################
#################################################################################
