# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 20:40:00 2024

@author: jonathan
"""

from typing import Union, Any

import pandas as pd
from qtpy import QtWidgets, QtCore

from ..devices import get_final_device_config

from ..elements import Variable as Variable_og
from ..variables import Variable

# Contains local import:
# from .monitoring.main import Monitor
# from .GUI_slider import Slider
# from .GUI_variables import VariablesMenu
# from .plotting.main import Plotter
# from .GUI_add_device import AddDeviceWindow
# from .GUI_about import AboutWindow
# Not yet or maybe never (too intertwined with mainGui) # from .scanning.main import Scanner


instances = {
    'monitors': {},
    'sliders': {},
    'variablesMenu': None,
    'plotter': None,
    'addDevice': None,
    'about': None,
    'preferences': None,
    'driverInstaller': None,
    # 'scanner': None,
}


# =============================================================================
# Monitor
# =============================================================================
def openMonitor(variable: Union[Variable, Variable_og],
                has_parent: bool = False):
    """ Opens the monitor associated to the variable. """
    from .monitoring.main import Monitor  # Inside to avoid circular import

    assert isinstance(variable, (Variable, Variable_og)), (
        f'Need type {Variable} or {Variable_og}, but given type is {type(variable)}')
    assert variable.readable, f"The variable {variable.address()} is not readable"

    # If the monitor is not already running, create one
    if id(variable) not in instances['monitors'].keys():
        instances['monitors'][id(variable)] = Monitor(variable, has_parent)
        instances['monitors'][id(variable)].show()
    # If the monitor is already running, just make as the front window
    else:
        monitor = instances['monitors'][id(variable)]
        monitor.setWindowState(
            monitor.windowState()
            & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        monitor.activateWindow()


def clearMonitor(variable: Union[Variable, Variable_og]):
    """ Clears monitor instances reference when quitted """
    if id(variable) in list(instances['monitors']):
        instances['monitors'].pop(id(variable))


def closeMonitors():
    for monitor in list(instances['monitors'].values()):
        monitor.close()


# =============================================================================
# Slider
# =============================================================================
def openSlider(variable: Union[Variable, Variable_og],
               gui: QtWidgets.QMainWindow = None,
               item: QtWidgets.QTreeWidgetItem = None):
    """ Opend the slider associated to this variable. """
    from .GUI_slider import Slider  # Inside to avoid circular import

    assert isinstance(variable, (Variable, Variable_og)), (
        f'Need type {Variable} or {Variable_og}, but given type is {type(variable)}')
    assert variable.writable, f"The variable {variable.address()} is not writable"

    # If the slider is not already running, create one
    if id(variable) not in instances['sliders'].keys():
        instances['sliders'][id(variable)] = Slider(variable, gui=gui, item=item)
        instances['sliders'][id(variable)].show()
    # If the slider is already running, just make as the front window
    else:
        slider = instances['sliders'][id(variable)]
        slider.setWindowState(
            slider.windowState()
            & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        slider.activateWindow()


def clearSlider(variable: Union[Variable, Variable_og]):
    """ Clears the slider instances reference when quitted """
    if id(variable) in instances['sliders'].keys():
        instances['sliders'].pop(id(variable))


def closeSliders():
    for slider in list(instances['sliders'].values()):
        slider.close()


# =============================================================================
# VariableMenu
# =============================================================================
def openVariablesMenu(has_parent: bool = False):
    """ Opens the variables menu. """
    from .GUI_variables import VariablesMenu  # Inside to avoid circular import
    if instances['variablesMenu'] is None:
        instances['variablesMenu'] = VariablesMenu(has_parent)
        instances['variablesMenu'].show()
    else:
        instances['variablesMenu'].refresh()
        instances['variablesMenu'].setWindowState(
            instances['variablesMenu'].windowState()
            & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        instances['variablesMenu'].activateWindow()


def clearVariablesMenu():
    """ Clears the variables menu instance reference when quitted """
    instances['variablesMenu'] = None


def closeVariablesMenu():
    if instances['variablesMenu'] is not None:
        instances['variablesMenu'].close()


# =============================================================================
# Plotter
# =============================================================================
def openPlotter(variable: Union[Variable, Variable_og, pd.DataFrame, Any] = None,
                has_parent: bool = False):
    """ Opens the plotter. Can add variable. """
    from .plotting.main import Plotter  # Inside to avoid circular import
    # If the plotter is not already running, create one
    if instances['plotter'] is None:
        instances['plotter'] = Plotter(has_parent)
    # If the plotter is not active open it (keep data if closed)
    if not instances['plotter'].active:
        instances['plotter'].show()
        instances['plotter'].activateWindow()
        instances['plotter'].active = True
    # If the plotter is already running, just make as the front window
    else:
        instances['plotter'].setWindowState(
            instances['plotter'].windowState()
            & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        instances['plotter'].activateWindow()

    if variable is not None:
            instances['plotter'].refreshPlotData(variable)


def clearPlotter():
    """ Deactivates the plotter when quitted but keep the instance in memory """
    if instances['plotter'] is not None:
        instances['plotter'].active = False  # don't want to close plotter because want to keep data


def closePlotter():
    if instances['plotter'] is not None:
        instances['plotter'].figureManager.fig.deleteLater()
        for children in instances['plotter'].findChildren(QtWidgets.QWidget):
            children.deleteLater()

        instances['plotter'].close()
        instances['plotter'] = None  # To remove plotter from memory


# =============================================================================
# AddDevice
# =============================================================================
def openAddDevice(gui: QtWidgets.QMainWindow = None, name: str = ''):
    """ Opens the add device window. """
    from .GUI_add_device import AddDeviceWindow  # Inside to avoid circular import
    # If the add device window is not already running, create one
    if instances['addDevice'] is None:
        instances['addDevice'] = AddDeviceWindow(gui)
        instances['addDevice'].show()
        instances['addDevice'].activateWindow()
    # If the add device window is already running, just make as the front window
    else:
        instances['addDevice'].setWindowState(
            instances['addDevice'].windowState()
            & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        instances['addDevice'].activateWindow()

    # Modify existing device
    if name != '':
        try:
            conf = get_final_device_config(name)
        except Exception as e:
            instances['addDevice'].setStatus(str(e), 10000, False)
        else:
            instances['addDevice'].modify(name, conf)


def clearAddDevice():
    """ Clears the addDevice instance reference when quitted """
    instances['addDevice'] = None


def closeAddDevice():
    if instances['addDevice'] is not None:
        instances['addDevice'].close()


# =============================================================================
# About
# =============================================================================
def openAbout(gui: QtWidgets.QMainWindow = None):
    """ Opens the about window. """
    # If the about window is not already running, create one
    from .GUI_about import AboutWindow  # Inside to avoid circular import
    if instances['about'] is None:
        instances['about'] = AboutWindow(gui)
        instances['about'].show()
        instances['about'].activateWindow()
    # If the about window is already running, just make as the front window
    else:
        instances['about'].setWindowState(
            instances['about'].windowState()
            & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        instances['about'].activateWindow()


def clearAbout():
    """ Clears the about instance reference when quitted """
    instances['about'] = None


def closeAbout():
    if instances['about'] is not None:
        instances['about'].close()


# =============================================================================
# Preferences
# =============================================================================
def openPreferences(gui: QtWidgets.QMainWindow = None):
    """ Opens the preferences window. """
    # If the about window is not already running, create one
    from .GUI_preferences import PreferencesWindow  # Inside to avoid circular import
    if instances['preferences'] is None:
        instances['preferences'] = PreferencesWindow(gui)
        instances['preferences'].show()
        instances['preferences'].activateWindow()
    # If the about window is already running, just make as the front window
    else:
        instances['preferences'].setWindowState(
            instances['preferences'].windowState()
            & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        instances['preferences'].activateWindow()


def clearPreferences():
    """ Clears the preferences instance reference when quitted """
    instances['preferences'] = None


def closePreferences():
    if instances['preferences'] is not None:
        instances['preferences'].close()



# =============================================================================
# Driver installer
# =============================================================================
def openDriverInstaller(gui: QtWidgets.QMainWindow = None):
    """ Opens the driver installer. """
    # If the about window is not already running, create one
    from .GUI_driver_installer import DriverInstaller  # Inside to avoid circular import
    if instances['driverInstaller'] is None:
        instances['driverInstaller'] = DriverInstaller(gui)
        instances['driverInstaller'].show()
        instances['driverInstaller'].activateWindow()
    # If the about window is already running, just make as the front window
    else:
        instances['driverInstaller'].setWindowState(
            instances['driverInstaller'].windowState()
            & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        instances['driverInstaller'].activateWindow()


def clearDriverInstaller():
    """ Clears the driver unstaller instance reference when quitted """
    instances['driverInstaller'] = None


def closeDriverInstaller():
    if instances['driverInstaller'] is not None:
        instances['driverInstaller'].close()


# =============================================================================
# Scanner
# =============================================================================
# def openScanner(gui: QtWidgets.QMainWindow, show=True):
#     """ Opens the scanner. """
#     # If the scanner is not already running, create one
#     from .scanning.main import Scanner  # Inside to avoid circular import
#     if instances['scanner'] is None:
#         instances['scanner'] = Scanner(gui)
#         instances['scanner'].show()
#         instances['scanner'].activateWindow()
#         gui.activateWindow() # Put main window back to the front
#     # If the scanner is already running, just make as the front window
#     elif show:
#         instances['scanner'].setWindowState(
#             instances['scanner'].windowState()
#             & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
#         instances['scanner'].activateWindow()


# def clearScanner():
#     """ Clears the scanner instance reference when quitted """
#     instances['scanner'] = None


# def closeScanner():
#     if instances['scanner'] is not None:
#         instances['scanner'].close()
