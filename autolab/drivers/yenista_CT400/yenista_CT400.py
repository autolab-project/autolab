#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified): Yenista CT400.
-
"""

import sys
import os
import ctypes as ct

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


ADDRESS = 12
LOW_WAVELENGTH = 1510.
HIGH_WAVELENGTH = 1610.
SPEED = 100
RES = 5
WAVELENGTH = 1550.
POWER = 1.
STATE = DISABLE
LASER_MODEL = LS_TunicsPlus  # doesn't seems to bother execution
# LASER_MODEL = LS_TunicsT100s


class Laser:
    """ Contain all the ct400 commands related to the laser"""

    def __init__(self, dev):  # dev is the ct400 class
        self.dev = dev

        self._init_variables()

        try:
            self.connect()
        except:
            print("Connection to the laser failed")

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
        self._ADDRESS = ADDRESS
        self._LASER_MODEL = LASER_MODEL
        self._STATE = STATE
        self._POWER = POWER
        self._WAVELENGTH = WAVELENGTH
        self._LOW_WAVELENGTH = LOW_WAVELENGTH
        self._HIGH_WAVELENGTH = HIGH_WAVELENGTH
        self._RES = RES # Redondant with set_res

    def _init_laser(self):

        self.tcError = ct.create_string_buffer(1024)
        self.controller.CT400_SetLaser(self.uiHandle, LI_1, ENABLE, self._ADDRESS,
                             self._LASER_MODEL,
                             ct.c_double(self._LOW_WAVELENGTH),
                             ct.c_double(self._HIGH_WAVELENGTH),
                             SPEED)

        self.set_scan(self._POWER, self._LOW_WAVELENGTH, self._HIGH_WAVELENGTH)
        self.set_res(self._RES)


    def get_model(self):
        return self._LASER_MODEL

    def set_model(self, value):
        self._LASER_MODEL = int(value)
        self._init_laser()


    def get_address(self):
        return self._ADDRESS

    def set_address(self, value):
        self._ADDRESS = int(value)
        self._init_laser()


    def get_low_wavelength(self):
        return self._LOW_WAVELENGTH

    def set_low_wavelength(self, value):
        self.set_scan(self.get_power(), float(value), self.get_high_wavelength())


    def get_high_wavelength(self):
        return self._HIGH_WAVELENGTH

    def set_high_wavelength(self, value):
        self.set_scan(self.get_power(), self.get_low_wavelength(), float(value))

    def set_scan(self, power, low_wl, high_wl):
        self.controller.CT400_SetScan(
                self.uiHandle,
                ct.c_double(power),
                ct.c_double(low_wl),
                ct.c_double(high_wl))

        self._POWER = float(power)
        self._LOW_WAVELENGTH = float(low_wl)
        self._HIGH_WAVELENGTH = float(high_wl)

    def get_res(self):
        return self._RES

    def set_res(self, value):
        self._RES = int(value)
        self.controller.CT400_SetSamplingResolution(self.uiHandle, self._RES)


    def get_output_state(self):
        return self._STATE

    def set_output_state(self, state):
        value = ENABLE if state else DISABLE
        self._STATE = value

        self.controller.CT400_CmdLaser(self.uiHandle, LI_1, value,
                             ct.c_double(self.get_wavelength()), ct.c_double(self.get_power()))


    def get_wavelength(self):
        return self._WAVELENGTH

    def set_wavelength(self, value):
        self._WAVELENGTH = float(value)
        self.controller.CT400_CmdLaser(self.uiHandle, LI_1, self.get_output_state(),
                             ct.c_double(self._WAVELENGTH), ct.c_double(self.get_power()))


    def get_power(self):
        return self._POWER

    def set_power(self, value):
        self._POWER = float(value)
        self.controller.CT400_CmdLaser(self.uiHandle, LI_1, self.get_output_state(),
                             ct.c_double(self.get_wavelength()), ct.c_double(value))


    def do_sweep(self):
        self._STATE = ENABLE
        # uiHandle = self.uiHandle

        self.controller.CT400_SetDetectorArray(self.uiHandle, DISABLE, DISABLE, DISABLE, DISABLE)

        self.controller.CT400_SetBNC(self.uiHandle, DISABLE, ct.c_double(0.0), ct.c_double(0.0), Unit_mW)

        self.controller.CT400_SetScan(self.uiHandle, ct.c_double(self.get_power()),
                            ct.c_double(self.get_low_wavelength()),
                            ct.c_double(self.get_high_wavelength()))

        self.controller.CT400_ScanStart(self.uiHandle)

        iErrorID = self.controller.CT400_ScanWaitEnd(self.uiHandle, self.tcError)

        assert iErrorID == 0, 'Error during sweep: '+repr(self.tcError.value)[2:-1]


        self._get_data_sweep()


    def _get_data_sweep(self):
        # uiHandle = self.uiHandle

        iPointsNumber = self.controller.CT400_GetNbDataPoints(self.uiHandle)
        DataArraySize = ct.c_double * iPointsNumber
        (dWavelengthSync, dPowerSync, dDetector1Sync) = (DataArraySize(), DataArraySize(), DataArraySize())
        self.controller.CT400_ScanGetWavelengthSyncArray(self.uiHandle, ct.byref(dWavelengthSync), iPointsNumber)
        self.controller.CT400_ScanGetPowerSyncArray(self.uiHandle, ct.byref(dPowerSync), iPointsNumber)
        self.controller.CT400_ScanGetDetectorArray(self.uiHandle, DE_1, ct.byref(dDetector1Sync), iPointsNumber)

        # info: resample interpolate data to match the asked linspace
        # iPointsNumberResampled = self.controller.CT400_GetNbDataPointsResampled(self.uiHandle)
        # DataArraySizeResampled = ct.c_double * iPointsNumberResampled
        # (dWavelengthResampled, dPowerResampled, dDetector1Resampled) = (DataArraySizeResampled(), DataArraySizeResampled(), DataArraySizeResampled())
        # self.controller.CT400_ScanGetWavelengthResampledArray(self.uiHandle, ct.byref(dWavelengthResampled), iPointsNumberResampled)
        # self.controller.CT400_ScanGetPowerResampledArray(self.uiHandle, ct.byref(dPowerResampled), iPointsNumberResampled)
        # self.controller.CT400_ScanGetDetectorResampledArray(self.uiHandle, DE_1, ct.byref(dDetector1Resampled), iPointsNumberResampled)

        # dWavelengthSync = np.linspace(1510.2, 1610, 1001)  # used to test without the ct400
        # dPowerSync = np.random.random(dWavelengthSync.shape)
        # dDetector1Sync = np.random.random(dWavelengthSync.shape)

        # dWavelengthResampled = np.linspace(1510, 1610, 1001)  # used to test without the ct400
        # dPowerResampled = dPowerSync
        # dDetector1Resampled = dDetector1Sync

        results_raw = {"L": np.array(dWavelengthSync, dtype=float),
                        "O": np.array(dPowerSync, dtype=float),
                        "1": np.array(dDetector1Sync, dtype=float)}

        # results_interp = {"L": np.array(dWavelengthResampled, dtype=float),
        #                   "O": np.array(dPowerResampled, dtype=float),
        #                   "1": np.array(dDetector1Resampled, dtype=float)}

        data = {"Last Scan": pd.DataFrame(results_raw),
                # "Last Scan_interp": pd.DataFrame(results_interp)
                }

        self.dev.dev.data.update(data)
        self.dev.dev._last_data_name = "Last Scan"


    def get_data(self):
        return pd.DataFrame(self.dev.dev.data.get("Last Scan"))  # better to let Last Scan to avoid saving data from loaded data
        # return pd.DataFrame(self.dev.dev.data.get(self.dev.dev._last_data_name))


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
                       'help':'Set the first sweep wavelength in nm'})

        config.append({'element':'variable','name':'high_wavelength','unit':'nm','type':float,
                       'read':self.get_high_wavelength,'write':self.set_high_wavelength,
                       'help':'Set the last sweep wavelength in nm'})

        config.append({'element':'variable','name':'resolution','unit':'pm','type':int,
                       'read':self.get_res,'write':self.set_res,
                       'help':'Set the sweep wavelength resolution in pm'})

        config.append({'element':'action','name':'sweep','do':self.do_sweep,
                       'help':'Start the wavelength sweep with the previsouly set values'})

        config.append({'element':'action','name':'connect_laser','do':self.connect,
                       "help": "Try to connect to the laser"})

        config.append({'element':'variable','name':'laser_adress','type':int,
                       'read':self.get_address,'write':self.set_address,
                       "help": "Set the laser adress"})

        config.append({'element':'variable','name':'laser_model','type':int,
                       'read':self.get_model,'write':self.set_model,
                       "help": "Set the laser model \n(LS_TunicsPlus, LS_TunicsPurity, LS_TunicsReference, LS_TunicsT100s, LS_TunicsT100r, LS_JdsuSws, LS_Agilent, NB_SOURCE) \n(0, 1, 2, 3, 4, 5, 6, 7)"})

        config.append({'element':'variable','name':'data','type':pd.DataFrame,
                       'read':self.get_data,
                       "help": "Return the data stored"})

        return config


class Detectors:
    """ Contain only the ct400 commands related to the detectors (no laser commands)"""

    def __init__(self, dev, libpath):
        self.libpath = libpath

        self.dev = dev  # used by the laser

        try:
            self.connect()
        except:
            print("Connection to the ct400 failed")

    def connect(self):
        try:
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

        config.append({'element':'action','name':'connect_ct400','do':self.connect, "help": "Try to connect the ct400"})
        return config


    def close(self):
        self.controller.CT400_Close(self.uiHandle)



class Driver():

    def __init__(self, libpath):

        self.libpath = libpath

        self.data = dict()
        self._last_data_name = ""

        sys.path.append(os.path.dirname(__file__))
        from interface import Interface

        self.interface = Interface(self)

        self.detectors = Detectors(self, self.libpath)

        self.laser = Laser(self.detectors)


    def available_data(self):
        return list(self.data.keys())

    def disp_available_data(self):
        return str(self.available_data())

    def get_driver_model(self):

        config = []

        interface = self.__dict__.get("interface")
        if interface is not None:
            config.append({'element':'module','name':'interface','object':getattr(self,'interface')})

        config.append({'element':'module','name':'detectors','object':getattr(self,'detectors')})
        config.append({'element':'module','name':'laser','object':getattr(self,'laser')})
        config.append({'element':'variable','name':'available_data','read':self.disp_available_data,'type':str})
        return config


#################################################################################
############################## Connections classes ##############################
class Driver_DDL(Driver):
    def __init__(self,
        libpath=r"C:\Program Files (x86)\Yenista Optics\CT400\Library 1.3.2\Win64\CT400_lib.dll",
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
            "CT400_SwitchInput",
            "CT400_ResetCalibration",
            "CT400_UpdateCalibration",
            "CT400_SetExternalSynchronizationIN",
            "CT400_SetExternalSynchronization",
            "ScanGetLineDetectionArray",
            ## see CT400_PG.pdf for all commands and explainations
            ]

        Driver.__init__(self, libpath)


    def close(self):
        try:
            self.detectors.close()
        except:
            print("Warning, CT400 didn't close properly")

############################## Connections classes ##############################
#################################################################################
