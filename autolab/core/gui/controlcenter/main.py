# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 23:29:33 2017

@author: Quentin Chateiller
quentin.chateiller@c2n.upsaclay.fr

"""

import os

import autolab
from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QApplication
from ..scanning.main import Scanner

from ..ct400_interface.main import CT400Gui
from ..plotting.main import Plotter

from .thread import ThreadManager
from .treewidgets import TreeWidgetItemModule


class ControlCenter(QtWidgets.QMainWindow):

    def __init__(self):

        # Set up the user interface from Designer.
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__),'interface.ui')
        uic.loadUi(ui_path,self)

        # Window configuration
        self.setWindowTitle("AUTOLAB - Control Panel")
        self.setFocus()
        self.activateWindow()

        # Tree widget configuration
        self.tree.setHeaderLabels(['Objects','Type','Actions','Values',''])
        self.tree.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.tree.header().resizeSection(0, 200)
        self.tree.header().resizeSection(4, 15)

        self.tree.header().setStretchLastSection(False)
        self.tree.itemClicked.connect(self.itemClicked)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.rightClick)
        self.tree.setAlternatingRowColors(True)

        # Thread manager
        self.threadManager = ThreadManager(self)

        # Scanner / Monitors
        self.scanner = None
        self.plotter = None
        self.ct400_gui = None
        self.monitors = {}
        self.customGUIdict = {}

        # BUG: tooltip not displayed
        scanAction = self.menuBar.addAction('Open scanner')
        scanAction.triggered.connect(self.openScanner)
        scanAction.setToolTip('Open the scanner in another window')

        plotAction = self.menuBar.addAction('Open plotter')
        plotAction.triggered.connect(self.openPlotter)
        plotAction.setToolTip('Open the plotter in another window')


        ct400Action = self.menuBar.addAction('Open CT400 GUI')
        ct400Action.triggered.connect(self.openCT400Gui)
        ct400Action.setToolTip('Open the CT400 GUI in another window')

        reportAction = self.menuBar.addAction('Report bugs / suggestions')
        reportAction.triggered.connect(autolab.report)
        reportAction.setToolTip('Open the issue webpage of this project on GitHub')

        helpAction = self.menuBar.addAction('Help')
        helpAction.triggered.connect(autolab.doc)
        helpAction.setToolTip('Open the documentation on Read The Docs website')

    def initialize(self):

        """ This function will create the first items in the tree, but will
        associate only the ones already loaded in autolab """

        for devName in autolab.list_local_configs() :
            item = TreeWidgetItemModule(self.tree,devName,self)
            for i in range(5) :
                item.setBackground(i, QtGui.QColor('#9EB7F5'))  # blue
            if devName in autolab.list_devices() :
                self.associate(item)



    def setStatus(self,message, timeout=0):

        """ Modify the message displayed in the status bar """

        self.statusbar.showMessage(message, msecs=timeout)



    def clearStatus(self):

        """ Erase the message displayed in the status bar """

        self.setStatus('')



    def rightClick(self,position):

        """ Function called when a right click has been detected in the tree """

        item = self.tree.itemAt(position)
        if hasattr(item,'menu') :
            item.menu(position)






    def itemClicked(self,item):

        """ Function called when a normal click has been detected in the tree.
            Check the association if it is a main item """

        if item.parent() is None and item.loaded is False :
            self.associate(item)
            item.setExpanded(True)



    def associate(self,item):

        """ Function called to associate a main module to one item in the tree """

        # Try to get / instantiated the device
        check = False
        try :
            self.setStatus(f'Loading device {item.name}...', 5000)
            module = autolab.get_device(item.name)

            # If the driver has an openGUI method, a button will be added to the Autolab menu to access it.
            if hasattr(module.instance, "openGUI"):
                if hasattr(module.instance, "gui_name"):
                    gui_name = str(module.instance.gui_name)
                else:
                    gui_name = 'Custom GUI'

                customButton = self.customGUIdict.get(gui_name, None)

                if customButton is None:
                    customButton = self.menuBar.addAction(gui_name)
                    self.customGUIdict[gui_name] = customButton

                customButton.triggered.disconnect()
                customButton.triggered.connect(module.instance.openGUI)

            check = True
            self.clearStatus()
        except Exception as e :
            self.setStatus(f'An error occured when loading device {item.name} : {str(e)}', 10000)

        # If success, load the entire module (submodules, variables, actions)
        if check is True :
            item.load(module)



    def openCT400Gui(self):

        """ This function open the CT400 GUI associated to this variable. """
        # TODO: merge CT400GUI into Plotter and integrate plotting.analyze as standalone GUI feature (no driver)
        # If the scanner is not already running, create one
        if self.ct400_gui is None:

            list_devices_gui = [devName for devName in autolab.list_local_configs()]  # All devices
            check_list_gui = [bool(str(x).lower().startswith("ct400")) for x in list_devices_gui]

            for i, check in enumerate(check_list_gui):  # Index of first ct400 find
                if check:
                    break
            else:
                i = None

            if i is not None:  # If find a ct400 device
                ct400_name = list_devices_gui[i]

                if ct400_name not in autolab.list_devices():  # If not in connected devices connect ct400
                    ct400_tree = self.tree.findItems(ct400_name, QtCore.Qt.MatchExactly)[0]
                    self.associate(ct400_tree)
                    ct400_tree.setExpanded(True)

                ct400 = autolab.DEVICES.get(ct400_name)
                if ct400 is not None:
                    self.ct400_gui = CT400Gui(self, ct400)
                    self.ct400_gui.show()
                    self.ct400_gui.activateWindow()

            else:
                self.setStatus(f'No CT400 found in the devices list: {list_devices_gui}', 10000)

        # If the CT400 GUI is already running, just make as the front window
        else :
            self.ct400_gui.setWindowState(self.ct400_gui.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.ct400_gui.activateWindow()

    def openScanner(self):

        """ This function open the scanner associated to this variable. """

        # If the scanner is not already running, create one
        if self.scanner is None :
            self.scanner = Scanner(self)
            self.scanner.show()
            self.scanner.activateWindow()
            self.activateWindow() # Put main window back to the front


        # If the scanner is already running, just make as the front window
        else :
            self.scanner.setWindowState(self.scanner.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.scanner.activateWindow()


    def openPlotter(self):

        """ This function open the plotter associated to this variable. """

        # If the scanner is not already running, create one
        if self.plotter is None:
            self.plotter = Plotter(self)
        # If the plotter is not active open it (keep data if closed)
        if not self.plotter.active:
            self.plotter.show()
            self.plotter.activateWindow()
            self.plotter.active = True
        # If the scanner is already running, just make as the front window
        else :
            self.plotter.setWindowState(self.plotter.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.plotter.activateWindow()



    def setScanParameter(self,variable):

        if self.scanner is None :
            self.openScanner()

        self.scanner.configManager.setParameter(variable)


    def addStepToScanRecipe(self,stepType,element):

        if self.scanner is None :
            self.openScanner()

        self.scanner.configManager.addRecipeStep(stepType,element)


    def clearScanner(self):

        """ This clear the gui instance reference when quitted """

        self.scanner = None

    def clearPlotter(self):

        """ This deactivate the plotter when quitted but keep the instance in memory """
        if self.plotter is not None:
            self.plotter.active = False  # don't want to close plotter because want to keep data

    def clearCT400(self):

        """ This clear the gui instance reference when quitted """

        self.ct400_gui = None


    def closeEvent(self,event):

        """ This function does some steps before the window is really killed """

        if self.scanner is not None :
            self.scanner.close()

        if self.plotter is not None :
            self.plotter.close()

        if self.ct400_gui is not None :
            self.ct400_gui.close()

        monitors = list(self.monitors.values())
        for monitor in monitors:
            monitor.close()

        autolab.close()  # close all devices

        QApplication.quit()  # close the control center interface
