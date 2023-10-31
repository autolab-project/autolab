# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 23:29:33 2017

@author: Quentin Chateiller
quentin.chateiller@c2n.upsaclay.fr

"""

import os
import sys

from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QApplication

from .thread import ThreadManager
from .treewidgets import TreeWidgetItemModule
from ..scanning.main import Scanner
from ..plotting.main import Plotter
from ... import devices, web, paths, config


class OutputWrapper(QtCore.QObject):
    """ https://stackoverflow.com/questions/19855288/duplicate-stdout-stderr-in-qtextedit-widget """
    outputWritten = QtCore.pyqtSignal(object, object)

    def __init__(self, parent, stdout=True, logger_active=False, print_active=True):
        super().__init__(parent)
        if stdout:
            self._stream = sys.stdout
            sys.stdout = self
        else:
            self._stream = sys.stderr
            sys.stderr = self
        self._stdout = stdout
        self.logger_active = logger_active
        self.print_active = print_active

    def write(self, text):
        if self.print_active: self._stream.write(text)
        if self.logger_active: self.outputWritten.emit(text, self._stdout)

    def __getattr__(self, name):
        return getattr(self._stream, name)

    def __del__(self):
        try:
            if self._stdout:
                sys.stdout = self._stream
            else:
                sys.stderr = self._stream
        except AttributeError:
            pass


class ControlCenter(QtWidgets.QMainWindow):

    def __init__(self):

        # Set up the user interface from Designer.
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__),'interface.ui')
        uic.loadUi(ui_path,self)

        # Import Autolab config
        control_center_config = config.get_control_center_config()
        logger_active = control_center_config['logger']
        if logger_active == "True":
            logger_active = True
        elif logger_active == "False":
            logger_active = False
        else:
            logger_active = bool(int(float(logger_active)))
        print_active = control_center_config['print']
        if print_active == "True":
            print_active = True
        elif print_active == "False":
            print_active = False
        else:
            print_active = bool(int(float(print_active)))

        # Set logger
        self.stdout = OutputWrapper(self, True, logger_active, print_active)
        self.stderr = OutputWrapper(self, False, logger_active, print_active)
        if logger_active:
            self.logger = QtWidgets.QTextBrowser(self)
            self.loggerDefaultColor = self.logger.textColor()
            # self.verticalLayout.addWidget(self.logger)
            self.splitter.insertWidget(1, self.logger)
            self.splitter.setSizes([500,100])
            self.stdout.outputWritten.connect(self.handleOutput)
            self.stderr.outputWritten.connect(self.handleOutput)

        # Window configuration
        self.setWindowTitle("AUTOLAB - Control Panel")
        self.setFocus()
        self.activateWindow()

        # Tree widget configuration
        self.tree.last_drag = None
        self.tree.gui = self
        self.tree.setHeaderLabels(['Objects','Type','Actions','Values',''])
        self.tree.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.tree.header().resizeSection(0, 200)
        self.tree.header().resizeSection(4, 15)
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.tree.header().setStretchLastSection(False)
        self.tree.itemClicked.connect(self.itemClicked)
        self.tree.itemPressed.connect(self.itemPressed)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.rightClick)
        self.tree.setAlternatingRowColors(True)

        # Thread manager
        self.threadManager = ThreadManager(self)

        # Scanner / Monitors
        self.scanner = None
        self.plotter = None
        self.monitors = {}
        self.sliders = {}
        self.customGUIdict = {}
        self.threadModuleDict = {}
        self.threadItemDict = {}

        scanAction = self.menuBar.addAction('Open scanner')
        scanAction.triggered.connect(self.openScanner)
        scanAction.setStatusTip('Open the scanner in another window')

        plotAction = self.menuBar.addAction('Open plotter')
        plotAction.triggered.connect(self.openPlotter)
        plotAction.setStatusTip('Open the plotter in another window')

        # Settings menu
        settingsMenu = self.menuBar.addMenu('Settings')

        autolabConfig = settingsMenu.addAction('Autolab config')
        autolabConfig.triggered.connect(self.openAutolabConfig)
        autolabConfig.setStatusTip("Open the Autolab configuration file")

        devicesConfig = settingsMenu.addAction('Devices config')
        devicesConfig.triggered.connect(self.openDevicesConfig)
        devicesConfig.setStatusTip("Open the devices configuration file")

        plotterConfig = settingsMenu.addAction('Plotter config')
        plotterConfig.triggered.connect(self.openPlotterConfig)
        plotterConfig.setStatusTip("Open the plotter configuration file")

        # Help menu
        helpMenu = self.menuBar.addMenu('Help')

        reportAction = helpMenu.addAction('Report bugs / suggestions')
        reportAction.setIcon(QtGui.QIcon("bug.png"))
        reportAction.triggered.connect(web.report)
        reportAction.setStatusTip('Open the issue webpage of this project on GitHub')

        helpAction = helpMenu.addAction('Documentation')
        helpAction.triggered.connect(lambda : web.doc('default'))
        helpAction.setStatusTip('Open the documentation on Read The Docs website')

        self.timerDevice = QtCore.QTimer(self)
        self.timerDevice.setInterval(50) # ms
        self.timerDevice.timeout.connect(self.timerAction)

    def handleOutput(self, text, stdout):
        if not stdout: self.logger.setTextColor(QtCore.Qt.red)
        self.logger.insertPlainText(text)
        self.logger.moveCursor(QtGui.QTextCursor.End)
        self.logger.setTextColor(self.loggerDefaultColor)

    def timerAction(self):

        """ This function checks if a module has been loaded and put to the queue. If so, associate item and module """

        threadItemDictTemp = self.threadItemDict.copy()
        threadModuleDictTemp = self.threadModuleDict.copy()

        for item_id in threadModuleDictTemp.keys():

            item = threadItemDictTemp[item_id]
            module = threadModuleDictTemp[item_id]

            self.associate(item, module)
            item.setExpanded(True)

            self.threadItemDict.pop(item_id)
            self.threadModuleDict.pop(item_id)

        if len(threadItemDictTemp) == 0:
            self.timerDevice.stop()

    def initialize(self):

        """ This function will create the first items in the tree, but will
        associate only the ones already loaded in autolab """

        for devName in devices.list_devices() :
            item = TreeWidgetItemModule(self.tree,devName,self)
            for i in range(5) :
                item.setBackground(i, QtGui.QColor('#9EB7F5'))  # blue
            if devName in devices.list_loaded_devices() :
                self.itemClicked(item)


    def setStatus(self,message, timeout=0, stdout=True):

        """ Modify the message displayed in the status bar and add error message to logger """

        self.statusBar.showMessage(message, msecs=timeout)
        if not stdout: print(message, file=sys.stderr)


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

        if item.parent() is None and item.loaded is False and id(item) not in self.threadItemDict.keys():
            self.threadItemDict[id(item)] = item  # needed before start of timer to avoid bad timing and to stop thread before loading is done
            self.threadManager.start(item,'load')  # load device and add it to queue for timer to associate it later (doesn't block gui while device is openning)
            self.timerDevice.start()

    def itemPressed(self,item):

        """ Function called when a click (not released) has been detected in the tree.
            Store last dragged variable in tree so scanner can know it when it is dropped there """

        if hasattr(item, "module"):
            if item.is_not_submodule:
                self.tree.last_drag = item.name
            else:
                self.tree.last_drag = None
        elif hasattr(item, "variable"):
            self.tree.last_drag = item.variable
        elif hasattr(item, "action"):
            self.tree.last_drag = item.action
        else:
            self.tree.last_drag = None


    def associate(self,item, module):

        """ Function called to associate a main module to one item in the tree """

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

        # load the entire module (submodules, variables, actions)
        item.load(module)

        read_init_list = module._read_init_list
        for mod in module._mod.values():
            read_init_list.extend(mod._read_init_list)
        for variable in read_init_list:
            try:
                variable()
            except:
                self.setStatus(f"Can't read variable {variable.address()} on instantiation", 10000, False)


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


    def openAutolabConfig(self):
        """ Open the Autolab configuration file """
        os.startfile(paths.AUTOLAB_CONFIG)


    def openDevicesConfig(self):
        """ Open the devices configuration file """
        os.startfile(paths.DEVICES_CONFIG)

    def openPlotterConfig(self):
        """ Open the plotter configuration file """
        os.startfile(paths.PLOTTER_CONFIG)


    def setScanParameter(self,variable):

        if self.scanner is None :
            self.openScanner()

        self.scanner.configManager.setParameter(variable)


    def addStepToScanRecipe(self,stepType,element, recipe_name='recipe'):

        if self.scanner is None :
            self.openScanner()

        self.scanner.configManager.addRecipeStep(stepType,element, recipe_name=recipe_name)


    def clearScanner(self):

        """ This clear the gui instance reference when quitted """

        self.scanner = None

    def clearPlotter(self):

        """ This deactivate the plotter when quitted but keep the instance in memory """
        if self.plotter is not None:
            self.plotter.active = False  # don't want to close plotter because want to keep data


    def closeEvent(self,event):

        """ This function does some steps before the window is really killed """

        if self.scanner is not None :
            self.scanner.close()

        if self.plotter is not None :
            self.plotter.close()

        monitors = list(self.monitors.values())
        for monitor in monitors:
            monitor.close()

        sliders = list(self.sliders.values())
        for slider in sliders:
            slider.close()

        devices.close()  # close all devices

        QApplication.quit()  # close the control center interface

        if hasattr(self, 'stdout'):
            sys.stdout = self.stdout._stream
            sys.stderr = self.stderr._stream
