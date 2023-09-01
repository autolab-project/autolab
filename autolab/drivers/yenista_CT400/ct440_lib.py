# =============================================================================
# Based on the example provided by EXFO with the CT440
# =============================================================================

from ctypes import windll, POINTER, c_int, c_int32, c_uint64, c_double, c_char_p
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


# Definition of the CT440 DLL class
class CT440:
    def __init__(self, libpath):

        # specify the path for the ct440 DLL.
        dll = windll.LoadLibrary(libpath)

        # Definition of DLL functions

        dll.CT440_Init.argtypes = [POINTER(c_int32)]
        dll.CT440_Init.restype = c_uint64
        self.init = dll.CT440_Init

        dll.CT440_CheckConnected.argtypes = [c_uint64]
        dll.CT440_CheckConnected.restype = c_int32
        self.check_connected = dll.CT440_CheckConnected

        dll.CT440_GetNbInputs.argtypes = [c_uint64]
        dll.CT440_GetNbInputs.restype = c_int32
        self.get_nb_inputs = dll.CT440_GetNbInputs

        dll.CT440_GetNbDetectors.argtypes = [c_uint64]
        dll.CT440_GetNbDetectors.restype = c_int32
        self.get_nb_detectors = dll.CT440_GetNbDetectors

        dll.CT440_GetCT440Type.argtypes = [c_uint64]
        dll.CT440_GetCT440Type.restype = c_int32
        self.get_ct_type = dll.CT440_GetCT440Type

        dll.CT440_GetCT440Model.argtypes = [c_uint64]
        dll.CT440_GetCT440Model.restype = c_int32
        self.get_ct440_model = dll.CT440_GetCT440Model

        dll.CT440_GetCT440SN.argtypes = [c_uint64, c_char_p]
        dll.CT440_GetCT440SN.restype = c_int32
        self.get_ct440_SN = dll.CT440_GetCT440SN

        dll.CT440_GetCT440DSPver.argtypes = [c_uint64, POINTER(c_int32)]
        dll.CT440_GetCT440DSPver.restype = c_int32
        self.get_ct440_DSPver = dll.CT440_GetCT440DSPver

        dll.CT440_SetLaser.argtypes = [c_uint64, rLaserInput, rEnable, c_int32, c_int32, rLaserSource, c_double, c_double, c_int32 ]
        dll.CT440_SetLaser.restype = c_int32
        self.set_laser = dll.CT440_SetLaser

        dll.CT440_SetScan.argtypes = [c_uint64, c_double, c_double, c_double, POINTER(c_int32) ]
        dll.CT440_SetScan.restype = c_int32
        self.set_scan = dll.CT440_SetScan

        dll.CT440_SetDetectorArray.argtypes = [c_uint64, rEnable, rEnable, rEnable, rEnable ]
        dll.CT440_SetDetectorArray.restype = c_int32
        self.set_detector_array = dll.CT440_SetDetectorArray

        dll.CT440_SetBNC.argtypes = [c_uint64, rEnable, c_double, c_double, rUnit ]
        dll.CT440_SetBNC.restype = c_int32
        self.set_bnc = dll.CT440_SetBNC

        dll.CT440_SetExternalSynchronization.argtypes = [c_uint64, rEnable]
        dll.CT440_SetExternalSynchronization.restype = c_int32
        self.set_external_synchronization = dll.CT440_SetExternalSynchronization

        dll.CT440_SetExternalSynchronizationIN.argtypes = [c_uint64, rEnable]
        dll.CT440_SetExternalSynchronizationIN.restype = c_int32
        self.set_external_synchronizationIn = dll.CT440_SetExternalSynchronizationIN

        dll.CT440_ScanStart.argtypes = [c_uint64, rEnable]
        dll.CT440_ScanStart.restype = c_int32
        self.scan_start = dll.CT440_ScanStart

        dll.CT440_ScanWaitEnd.argtypes = [c_uint64, c_char_p]
        dll.CT440_ScanWaitEnd.restype = c_int32
        self.scan_wait_end = dll.CT440_ScanWaitEnd

        dll.CT440_GetNbDataPoints.argtypes = [c_uint64, POINTER(c_int32), POINTER(c_int32)]
        dll.CT440_GetNbDataPoints.restype = c_int32
        self.get_nb_datapoints = dll.CT440_GetNbDataPoints

        dll.CT440_GetNbDataPointsResampled.argtypes = [c_uint64]
        dll.CT440_GetNbDataPointsResampled.restype = c_int32
        self.get_nb_datapoints_resampled = dll.CT440_GetNbDataPointsResampled

        dll.CT440_GetNbLinesDetected.argtypes = [c_uint64]
        dll.CT440_GetNbLinesDetected.restype = c_int32
        self.get_nb_lines_detected = dll.CT440_GetNbLinesDetected

        dll.CT440_ScanGetLinesDetectionArray.argtypes = [c_uint64, POINTER(c_double), c_int32]
        dll.CT440_ScanGetLinesDetectionArray.restype = c_int32
        self.scan_get_lines_detection_array = dll.CT440_ScanGetLinesDetectionArray

        dll.CT440_ScanGetWavelengthSyncArray.argtypes = [c_uint64, POINTER(c_double), c_int32]
        dll.CT440_ScanGetWavelengthSyncArray.restype = c_int32
        self.scan_get_wavelength_sync_array = dll.CT440_ScanGetWavelengthSyncArray

        dll.CT440_ScanGetWavelengthResampledArray.argtypes = [c_uint64, POINTER(c_double), c_int32]
        dll.CT440_ScanGetWavelengthResampledArray.restype = c_int32
        self.scan_get_wavelength_resampled_array = dll.CT440_ScanGetWavelengthResampledArray

        dll.CT440_ScanGetPowerSyncArray.argtypes = [c_uint64, POINTER(c_double), c_int32]
        dll.CT440_ScanGetPowerSyncArray.restype = c_int32
        self.scan_get_power_sync_array = dll.CT440_ScanGetPowerSyncArray

        dll.CT440_ScanGetPowerResampledArray.argtypes = [c_uint64, POINTER(c_double), c_int32]
        dll.CT440_ScanGetPowerResampledArray.restype = c_int32
        self.scan_get_power_resampled_array = dll.CT440_ScanGetPowerResampledArray

        dll.CT440_ScanGetDetectorArray.argtypes = [c_uint64, rDetector, POINTER(c_double), c_int32]
        dll.CT440_ScanGetDetectorArray.restype = c_int32
        self.scan_get_detector_array = dll.CT440_ScanGetDetectorArray

        dll.CT440_ScanGetDetectorResampledArray.argtypes = [c_uint64, rDetector, POINTER(c_double), c_int32]
        dll.CT440_ScanGetDetectorResampledArray.restype = c_int32
        self.scan_get_detector_resampled_array = dll.CT440_ScanGetDetectorResampledArray

        dll.CT440_ScanSaveWavelengthSyncFile.argtypes = [c_uint64, c_char_p]
        dll.CT440_ScanSaveWavelengthSyncFile.restype = c_int32
        self.scan_save_wavelength_sync_file = dll.CT440_ScanSaveWavelengthSyncFile

        dll.CT440_ScanSaveWavelengthResampledFile.argtypes = [c_uint64, c_char_p]
        dll.CT440_ScanSaveWavelengthResampledFile.restype = c_int32
        self.scan_save_wavelength_resampled_file = dll.CT440_ScanSaveWavelengthResampledFile

        dll.CT440_ScanSavePowerSyncFile.argtypes = [c_uint64, c_char_p]
        dll.CT440_ScanSavePowerSyncFile.restype = c_int32
        self.scan_save_power_sync_file = dll.CT440_ScanSavePowerSyncFile

        dll.CT440_ScanSavePowerResampledFile.argtypes = [c_uint64, c_char_p]
        dll.CT440_ScanSavePowerResampledFile.restype = c_int32
        self.scan_save_power_resampled_file = dll.CT440_ScanSavePowerResampledFile

        dll.CT440_ScanSaveDetectorFile.argtypes = [c_uint64, rDetector, c_char_p]
        dll.CT440_ScanSaveDetectorFile.restype = c_int32
        self.scan_save_detector_file = dll.CT440_ScanSaveDetectorFile

        dll.CT440_ScanSaveDetectorResampledFile.argtypes = [c_uint64, rDetector, c_char_p]
        dll.CT440_ScanSaveDetectorResampledFile.restype = c_int32
        self.scan_save_detector_resampled_file = dll.CT440_ScanSaveDetectorResampledFile

        dll.CT440_UpdateCalibration.argtypes = [c_uint64, rDetector]
        dll.CT440_UpdateCalibration.restype = c_int32
        self.update_calibration = dll.CT440_UpdateCalibration

        dll.CT440_UpdateWavelengthReference.argtypes = [c_uint64, c_double, c_double]
        dll.CT440_UpdateWavelengthReference.restype = c_int32
        self.update_wavelength_reference = dll.CT440_UpdateWavelengthReference

        dll.CT440_ResetCalibration.argtypes = [c_uint64]
        dll.CT440_ResetCalibration.restype = c_int32
        self.reset_calibration = dll.CT440_ResetCalibration

        dll.CT440_SwitchInput.argtypes = [c_uint64, rLaserInput]
        dll.CT440_SwitchInput.restype = c_int32
        self.switch_input = dll.CT440_SwitchInput

        dll.CT440_ReadPowerDetectors.argtypes = [c_uint64, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
        dll.CT440_ReadPowerDetectors.restype = c_int32
        self.read_power_detectors = dll.CT440_ReadPowerDetectors

        dll.CT440_CmdLaser.argtypes = [c_uint64, rLaserInput, rEnable, c_double, c_double]
        dll.CT440_CmdLaser.restype = c_int32
        self.cmd_laser = dll.CT440_CmdLaser

        dll.CT440_Polstate.argtypes = [c_uint64, c_int]
        dll.CT440_Polstate.restype = c_int32
        self.polstate = dll.CT440_Polstate

        dll.CT440_Close.argtypes = [c_uint64]
        dll.CT440_Close.restype = c_int32
        self.close = dll.CT440_Close

        dll.CT440_ScanGetProgress.argtypes = [c_uint64, rLaserInput, POINTER(c_int32), POINTER(c_int32), POINTER(c_int32), c_char_p]
        dll.CT440_ScanGetProgress.restype = c_int32
        self.scan_get_progress = dll.CT440_ScanGetProgress

        dll.CT440_ScanAbort.argtypes = [c_uint64]
        dll.CT440_ScanAbort.restype = c_int32
        self.scan_abort = dll.CT440_ScanAbort

        dll.CT440_MeasureDark.argtypes = [c_uint64, rDetector]
        dll.CT440_MeasureDark.restype = c_int32
        self.measure_dark = dll.CT440_MeasureDark

        dll.CT440_ResetDark.argtypes = [c_uint64, rDetector]
        dll.CT440_ResetDark.restype = c_int32
        self.reset_dark = dll.CT440_ResetDark

        dll.CT440_CalcPDL4OneDET.argtypes = [c_uint64, c_int32, c_int32,
                                            POINTER(c_double), POINTER(c_double), POINTER(c_double),
                                            POINTER(c_double), POINTER(c_double), POINTER(c_double),
                                            POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_int32)]
        dll.CT440_CalcPDL4OneDET.restype = c_int32
        self.calc_pdl_4onedet = dll.CT440_CalcPDL4OneDET

        dll.CT440_SetLaser2.argtypes = [c_uint64, rLaserInput, rEnable, c_char_p, rLaserSource, c_double, c_double, c_int32]
        dll.CT440_SetLaser2.restype = c_int32
        self.set_laser2 = dll.CT440_SetLaser2
