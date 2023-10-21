# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:26:32 2019

@author: qchat
"""

import sip
from PyQt5 import QtCore

from ... import devices
from ... import drivers


class ThreadManager :

    """ This class is dedicated to manage the different threads,
    from their creation, to their deletion after they have been used """


    def __init__(self,gui):
        self.gui = gui
        self.threads = {}



    def start(self,item,intType,value=None):

        """ This function is called when a new thread is requested,
        for a particular intType interaction type """

        # GUI disabling
        item.setDisabled(True)

        if hasattr(item, "execButton"):
            item.execButton.setEnabled(False)
        if hasattr(item, "readButton"):
            item.readButton.setEnabled(False)
        if hasattr(item, "valueWidget"):
            item.valueWidget.setEnabled(False)

        # disabling valueWidget deselect item and select next one, need to disable all items and reenable item
        list_item = self.gui.tree.selectedItems()
        for item_selected in list_item:
                item_selected.setSelected(False)
        item.setSelected(True)

        # Status writing
        if intType == 'read' : status = f'Reading {item.variable.address()}...'
        elif intType == 'write' : status = f'Writing {item.variable.address()}...'
        elif intType == 'execute' : status = f'Executing {item.action.address()}...'
        elif intType == 'load' : status = f'Loading plugin {item.name}...'
        self.gui.setStatus(status)

        # Thread configuration
        thread = InteractionThread(item,intType,value)
        tid = id(thread)
        self.threads[tid] = thread
        thread.endSignal.connect(lambda error, x=tid : self.threadFinished(x,error))
        thread.finished.connect(lambda x=tid : self.delete(x))

        # Starting thread
        thread.start()


    def threadFinished(self,tid,error):

        """ This function is called when a thread has finished its job, with an error or not
        It updates the status bar of the GUI in consequence and enabled back the correspondig item """

        if error is None : self.gui.clearStatus()
        else : self.gui.setStatus(str(error), 10000, False)

        item = self.threads[tid].item

        item.setDisabled(False)

        if hasattr(item, "execButton"):
            if not sip.isdeleted(item.execButton):
                item.execButton.setEnabled(True)
        if hasattr(item, "readButton"):
            if not sip.isdeleted(item.readButton):
                item.readButton.setEnabled(True)
        if hasattr(item, "valueWidget"):
            if not sip.isdeleted(item.valueWidget):
                item.valueWidget.setEnabled(True)


    def delete(self,tid):

        """ This function is called when a thread is about to be deleted.
        This removes it from the dictionnary self.threads, for a complete deletion """

        self.threads.pop(tid)






class InteractionThread(QtCore.QThread):

    """ This class is dedicated to operation interaction with the devices, in a new thread """

    endSignal = QtCore.pyqtSignal(object)


    def __init__(self,item,intType,value):
        QtCore.QThread.__init__(self)
        self.item = item
        self.intType = intType
        self.value = value



    def run(self):

        """ Depending on the interaction type requested, this function reads or writes a variable,
        or execute an action. """

        error = None

        try :
            if self.intType == 'read' : self.item.variable()
            elif self.intType == 'write' :
                self.item.variable(self.value)
                if self.item.variable.readable : self.item.variable()
            elif self.intType == 'execute' :
                if self.value is not None :
                    self.item.action(self.value)
                else :
                    self.item.action()
            elif self.intType == 'load' :
                self.item.gui.threadItemDict[id(self.item)] = self.item  # needed before get_device so gui can know an item has been clicked and prevent from multiple clicks

                plugin_name = self.item.name
                device_config = devices.get_final_device_config(plugin_name)

                try:
                    instance = drivers.get_driver(device_config['driver'],
                                                  device_config['connection'],
                                                  **{ k:v for k,v in device_config.items() if k not in ['driver','connection']},
                                                  gui=self.item.gui)
                    module = devices.Device(plugin_name,instance)
                    self.item.gui.threadModuleDict[id(self.item)] = module
                except Exception:
                    instance = drivers.get_driver(device_config['driver'],
                                                  device_config['connection'],
                                                  **{ k:v for k,v in device_config.items() if k not in ['driver','connection']})
                    module = devices.Device(plugin_name,instance)
                    self.item.gui.threadModuleDict[id(self.item)] = module
        except Exception as e:
            error = e
            if self.intType == 'load' :
                error = f'An error occured when loading device {self.item.name} : {str(e)}'
                if id(self.item) in self.item.gui.threadItemDict.keys():
                    self.item.gui.threadItemDict.pop(id(self.item))
        self.endSignal.emit(error)
