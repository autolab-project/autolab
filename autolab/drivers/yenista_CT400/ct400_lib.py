# =============================================================================
# Based on the example provided by EXFO with the CT400
# =============================================================================

import os
from ctypes import windll, POINTER, c_int32, c_uint64, c_double, c_char_p
from enum import IntEnum


# Definition of various constants to use the same names as the C interface
class ctypesEnum(IntEnum):
    @classmethod
    def from_param(cls, obj) :
        return int(obj)

class rLaserSource(ctypesEnum) :
    LS_TunicsPlus = 0
    LS_TunicsPurity = 1
    LS_TunicsReference = 2
    LS_T100S_HP = 3
    LS_TunicsT100r = 4
    LS_T200S = 5
    NB_SOURCE = 6

class rLaserInput(ctypesEnum) :
    LI_1 = 1
    LI_2 = 2
    LI_3 = 3
    LI_4 = 4

class rDetector(ctypesEnum) :
    DE_1 = 1
    DE_2 = 2
    DE_3 = 3
    DE_4 = 4
    DE_5 = 5

class rEnable(ctypesEnum) :
    DISABLE = 0
    ENABLE = 1

class rUnit(ctypesEnum) :
     Unit_mW = 0
     Unit_dBm = 1


# Definition of the CT400 DLL class
class CT400:
    def __init__(self, libpath):

        # specify the path for the CT400 DLL.
        windll.LoadLibrary(os.path.join(os.path.dirname(libpath), "SiUSBXp.dll"))  # ct400 only and not always necessary
        dll = windll.LoadLibrary(libpath)

        # Definition of DLL functions

        dll.CT400_Init.argtypes = [POINTER(c_int32)]
        dll.CT400_Init.restype = c_uint64
        self.init = dll.CT400_Init

        dll.CT400_CheckConnected.argtypes = [c_uint64]
        dll.CT400_CheckConnected.restype = c_int32
        self.check_connected = dll.CT400_CheckConnected

        dll.CT400_GetNbInputs.argtypes = [c_uint64]
        dll.CT400_GetNbInputs.restype = c_int32
        self.get_nb_inputs = dll.CT400_GetNbInputs

        dll.CT400_GetNbDetectors.argtypes = [c_uint64]
        dll.CT400_GetNbDetectors.restype = c_int32
        self.get_nb_detectors = dll.CT400_GetNbDetectors

        dll.CT400_GetCT400Type.argtypes = [c_uint64]
        dll.CT400_GetCT400Type.restype = c_int32
        self.get_ct_type = dll.CT400_GetCT400Type

        dll.CT400_SetLaser.argtypes = [c_uint64, rLaserInput, rEnable, c_int32, rLaserSource, c_double, c_double, c_int32 ]
        dll.CT400_SetLaser.restype = c_int32
        self.set_laser = dll.CT400_SetLaser

        dll.CT400_SetScan.argtypes = [c_uint64, c_double, c_double, c_double]
        dll.CT400_SetScan.restype = c_int32
        self.set_scan = dll.CT400_SetScan

        dll.CT400_SetSamplingResolution.argtypes = [c_uint64, c_uint64]
        dll.CT400_SetSamplingResolution.restype = c_int32
        self.set_resolution = dll.CT400_SetSamplingResolution

        dll.CT400_SetDetectorArray.argtypes = [c_uint64, rEnable, rEnable, rEnable, rEnable ]
        dll.CT400_SetDetectorArray.restype = c_int32
        self.set_detector_array = dll.CT400_SetDetectorArray

        dll.CT400_SetBNC.argtypes = [c_uint64, rEnable, c_double, c_double, rUnit ]
        dll.CT400_SetBNC.restype = c_int32
        self.set_bnc = dll.CT400_SetBNC

        dll.CT400_SetExternalSynchronization.argtypes = [c_uint64, rEnable]
        dll.CT400_SetExternalSynchronization.restype = c_int32
        self.set_external_synchronization = dll.CT400_SetExternalSynchronization

        dll.CT400_SetExternalSynchronizationIN.argtypes = [c_uint64, rEnable]
        dll.CT400_SetExternalSynchronizationIN.restype = c_int32
        self.set_external_synchronizationIn = dll.CT400_SetExternalSynchronizationIN

        dll.CT400_ScanStart.argtypes = [c_uint64]
        dll.CT400_ScanStart.restype = c_int32
        self.scan_start = dll.CT400_ScanStart

        dll.CT400_ScanWaitEnd.argtypes = [c_uint64, c_char_p]
        dll.CT400_ScanWaitEnd.restype = c_int32
        self.scan_wait_end = dll.CT400_ScanWaitEnd

        dll.CT400_GetNbDataPoints.argtypes = [c_uint64]
        dll.CT400_GetNbDataPoints.restype = c_int32
        self.get_nb_datapoints = dll.CT400_GetNbDataPoints

        dll.CT400_GetNbDataPointsResampled.argtypes = [c_uint64]
        dll.CT400_GetNbDataPointsResampled.restype = c_int32
        self.get_nb_datapoints_resampled = dll.CT400_GetNbDataPointsResampled

        dll.CT400_GetNbLinesDetected.argtypes = [c_uint64]
        dll.CT400_GetNbLinesDetected.restype = c_int32
        self.get_nb_lines_detected = dll.CT400_GetNbLinesDetected

        dll.CT400_ScanGetLinesDetectionArray.argtypes = [c_uint64, POINTER(c_double), c_int32]
        dll.CT400_ScanGetLinesDetectionArray.restype = c_int32
        self.scan_get_lines_detection_array = dll.CT400_ScanGetLinesDetectionArray

        dll.CT400_ScanGetWavelengthSyncArray.argtypes = [c_uint64, POINTER(c_double), c_int32]
        dll.CT400_ScanGetWavelengthSyncArray.restype = c_int32
        self.scan_get_wavelength_sync_array = dll.CT400_ScanGetWavelengthSyncArray

        dll.CT400_ScanGetWavelengthResampledArray.argtypes = [c_uint64, POINTER(c_double), c_int32]
        dll.CT400_ScanGetWavelengthResampledArray.restype = c_int32
        self.scan_get_wavelength_resampled_array = dll.CT400_ScanGetWavelengthResampledArray

        dll.CT400_ScanGetPowerSyncArray.argtypes = [c_uint64, POINTER(c_double), c_int32]
        dll.CT400_ScanGetPowerSyncArray.restype = c_int32
        self.scan_get_power_sync_array = dll.CT400_ScanGetPowerSyncArray

        dll.CT400_ScanGetPowerResampledArray.argtypes = [c_uint64, POINTER(c_double), c_int32]
        dll.CT400_ScanGetPowerResampledArray.restype = c_int32
        self.scan_get_power_resampled_array = dll.CT400_ScanGetPowerResampledArray

        dll.CT400_ScanGetDetectorArray.argtypes = [c_uint64, rDetector, POINTER(c_double), c_int32]
        dll.CT400_ScanGetDetectorArray.restype = c_int32
        self.scan_get_detector_array = dll.CT400_ScanGetDetectorArray

        dll.CT400_ScanGetDetectorResampledArray.argtypes = [c_uint64, rDetector, POINTER(c_double), c_int32]
        dll.CT400_ScanGetDetectorResampledArray.restype = c_int32
        self.scan_get_detector_resampled_array = dll.CT400_ScanGetDetectorResampledArray

        dll.CT400_ScanSaveWavelengthSyncFile.argtypes = [c_uint64, c_char_p]
        dll.CT400_ScanSaveWavelengthSyncFile.restype = c_int32
        self.scan_save_wavelength_sync_file = dll.CT400_ScanSaveWavelengthSyncFile

        dll.CT400_ScanSaveWavelengthResampledFile.argtypes = [c_uint64, c_char_p]
        dll.CT400_ScanSaveWavelengthResampledFile.restype = c_int32
        self.scan_save_wavelength_resampled_file = dll.CT400_ScanSaveWavelengthResampledFile

        dll.CT400_ScanSavePowerSyncFile.argtypes = [c_uint64, c_char_p]
        dll.CT400_ScanSavePowerSyncFile.restype = c_int32
        self.scan_save_power_sync_file = dll.CT400_ScanSavePowerSyncFile

        dll.CT400_ScanSavePowerResampledFile.argtypes = [c_uint64, c_char_p]
        dll.CT400_ScanSavePowerResampledFile.restype = c_int32
        self.scan_save_power_resampled_file = dll.CT400_ScanSavePowerResampledFile

        dll.CT400_ScanSaveDetectorFile.argtypes = [c_uint64, rDetector, c_char_p]
        dll.CT400_ScanSaveDetectorFile.restype = c_int32
        self.scan_save_detector_file = dll.CT400_ScanSaveDetectorFile

        dll.CT400_ScanSaveDetectorResampledFile.argtypes = [c_uint64, rDetector, c_char_p]
        dll.CT400_ScanSaveDetectorResampledFile.restype = c_int32
        self.scan_save_detector_resampled_file = dll.CT400_ScanSaveDetectorResampledFile

        dll.CT400_UpdateCalibration.argtypes = [c_uint64, rDetector]
        dll.CT400_UpdateCalibration.restype = c_int32
        self.update_calibration = dll.CT400_UpdateCalibration

        dll.CT400_ResetCalibration.argtypes = [c_uint64]
        dll.CT400_ResetCalibration.restype = c_int32
        self.reset_calibration = dll.CT400_ResetCalibration

        dll.CT400_SwitchInput.argtypes = [c_uint64, rLaserInput]
        dll.CT400_SwitchInput.restype = c_int32
        self.switch_input = dll.CT400_SwitchInput

        dll.CT400_ReadPowerDetectors.argtypes = [c_uint64, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
        dll.CT400_ReadPowerDetectors.restype = c_int32
        self.read_power_detectors = dll.CT400_ReadPowerDetectors

        dll.CT400_CmdLaser.argtypes = [c_uint64, rLaserInput, rEnable, c_double, c_double]
        dll.CT400_CmdLaser.restype = c_int32
        self.cmd_laser = dll.CT400_CmdLaser

        dll.CT400_Close.argtypes = [c_uint64]
        dll.CT400_Close.restype = c_int32
        self.close = dll.CT400_Close
