# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:26:32 2019

@author: qchat
"""

import sys
import inspect
from typing import Any

from qtpy import QtCore, QtWidgets

from ..GUI_utilities import qt_object_exists
from ...devices import get_final_device_config, list_loaded_devices, DEVICES, Device
from ...drivers import load_driver_lib, get_driver
from ...variables import update_allowed_dict


class ThreadManager:
    """ This class is dedicated to manage the different threads,
    from their creation, to their deletion after they have been used """
    def __init__(self, gui: QtWidgets.QMainWindow):
        self.gui = gui
        self.threads = {}
        self.threads_conn = {}

    def start(self, item: QtWidgets.QTreeWidgetItem, intType: str, value = None):
        """ This function is called when a new thread is requested,
        for a particular intType interaction type """
        # GUI disabling
        item.setDisabled(True)

        if hasattr(item, "execButton") and qt_object_exists(item.execButton):
            item.execButton.setEnabled(False)
        if hasattr(item, "readButton") and qt_object_exists(item.readButton):
            item.readButton.setEnabled(False)
        if hasattr(item, "valueWidget") and qt_object_exists(item.valueWidget):
            item.valueWidget.setEnabled(False)

        # disabling valueWidget deselect item and select next one, need to disable all items and reenable item
        for item_selected in self.gui.tree.selectedItems():
            item_selected.setSelected(False)

        item.setSelected(True)

        # Status writing
        if intType == 'read': status = f'Reading {item.variable.address()}...'
        elif intType == 'write': status = f'Writing {item.variable.address()}...'
        elif intType == 'execute': status = f'Executing {item.action.address()}...'
        elif intType == 'load': status = f'Loading device {item.name}...'
        self.gui.setStatus(status)

        # Thread configuration
        if intType == 'load':
            assert id(item) not in self.threads_conn
        thread = InteractionThread(item, intType, value)
        tid = id(thread)
        self.threads[tid] = thread
        if intType == 'load':
            self.threads_conn[id(item)] = tid

        thread.endSignal.connect(
            lambda error, x=tid: self.threadFinished(x, error))
        thread.finished.connect(lambda x=tid: self.delete(x))

        # Starting thread
        thread.start()

    def threadFinished(self, tid: int, error: Exception):
        """ This function is called when a thread has finished its job, with an error or not
        It updates the status bar of the GUI in consequence and enabled back the corresponding item """
        if error:
            if qt_object_exists(self.gui.statusBar):
                self.gui.setStatus(str(error), 10000, False)
            else:
                print(str(error), file=sys.stderr)

            if tid in self.threads_conn.values():
                item_id = list(self.threads_conn)[list(self.threads_conn.values()).index(tid)]
                if item_id in self.gui.threadItemDict:
                    self.gui.threadItemDict.pop(item_id)
        else:
            if qt_object_exists(self.gui.statusBar):
                self.gui.clearStatus()

        item = self.threads[tid].item
        if qt_object_exists(item):
            item.setDisabled(False)
            item.setValueKnownState(-1 if error else True)

        if hasattr(item, "execButton") and qt_object_exists(item.execButton):
            item.execButton.setEnabled(True)
        if hasattr(item, "readButton") and qt_object_exists(item.readButton):
            item.readButton.setEnabled(True)
        if hasattr(item, "valueWidget") and qt_object_exists(item.valueWidget):
            item.valueWidget.setEnabled(True)
            # Put back focus if item still selected (item.isSelected() doesn't work)
            if item in self.gui.tree.selectedItems():
                item.valueWidget.setFocus()

    def delete(self, tid: int):
        """ This function is called when a thread is about to be deleted.
        This removes it from the dictionnary self.threads, for a complete deletion """
        if self.threads[tid].intType == 'load':
            item_id = list(self.threads_conn)[list(self.threads_conn.values()).index(tid)]
            self.threads_conn.pop(item_id)
        self.threads.pop(tid)


class InteractionThread(QtCore.QThread):
    """ This class is dedicated to operation interaction with the devices, in a new thread """
    endSignal = QtCore.Signal(object)

    def __init__(self, item: QtWidgets.QTreeWidgetItem, intType: str, value: Any):
        super().__init__()
        self.item = item
        self.intType = intType
        self.value = value

    def run(self):
        """ Depending on the interaction type requested, this function reads or writes a variable,
        or execute an action. """
        error = None

        try:
            if self.intType == 'read': self.item.variable()
            elif self.intType == 'write':
                self.item.variable(self.value)
                if self.item.variable.readable: self.item.variable()
            elif self.intType == 'execute':
                if self.value is not None:
                    self.item.action(self.value)
                else:
                    self.item.action()
            # elif self.intType == 'load':
            #     # Note that threadItemDict needs to be updated outside of thread to avoid timing error
            #     module = devices.get_device(self.item.name)  # Try to get / instantiated the device
            #     self.item.gui.threadDeviceDict[id(self.item)] = module
            elif self.intType == 'load':  # OPTIMIZE: is very similar to get_device()
                # Note that threadItemDict needs to be updated outside of thread to avoid timing error
                device_name = self.item.name
                device_config = get_final_device_config(device_name)

                if device_name in list_loaded_devices():
                    assert device_config == DEVICES[device_name].device_config, 'You cannot change the configuration of an existing Device. Close it first & retry, or remove the provided configuration.'
                else:
                    driver_kwargs = {k: v for k, v in device_config.items() if k not in ['driver', 'connection']}
                    driver_lib = load_driver_lib(device_config['driver'])

                    if hasattr(driver_lib, 'Driver') and 'gui' in [param.name for param in inspect.signature(driver_lib.Driver.__init__).parameters.values()]:
                            driver_kwargs['gui'] = self.item.gui

                    instance = get_driver(
                        device_config['driver'], device_config['connection'],
                        **driver_kwargs)
                    DEVICES[device_name] = Device(
                        device_name, instance, device_config)
                    update_allowed_dict()

                self.item.gui.threadDeviceDict[id(self.item)] = DEVICES[device_name]

        except Exception as e:
            error = e
            if self.intType == 'load':
                error = f'An error occured when loading device {self.item.name}: {str(e)}'

        self.endSignal.emit(error)
