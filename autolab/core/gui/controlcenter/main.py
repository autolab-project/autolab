# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 23:29:33 2017

@author: Quentin Chateiller
quentin.chateiller@c2n.upsaclay.fr

"""

import sys
import queue
import time
import uuid
from typing import Any, Type

import numpy as np
import pandas as pd
from qtpy import QtCore, QtWidgets, QtGui
from qtpy.QtWidgets import QApplication

from .thread import ThreadManager
from .treewidgets import TreeWidgetItemModule
from ..scanning.main import Scanner
from ..plotting.main import Plotter
from ..variables import VARIABLES
from ..icons import icons
from ... import devices, web, paths, config, utilities


class OutputWrapper(QtCore.QObject):
    """ https://stackoverflow.com/questions/19855288/duplicate-stdout-stderr-in-qtextedit-widget """
    outputWritten = QtCore.Signal(object, object)

    def __init__(self, parent, stdout: bool = True,
                 logger_active: bool = False, print_active: bool = True):
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

    def write(self, text: str):
        if self.print_active: self._stream.write(text)
        if self.logger_active: self.outputWritten.emit(text, self._stdout)

    def __getattr__(self, name: str) -> Any:
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
    """ Main Qt window, Used to control devices, open scanner... """

    def __init__(self):

        # Set up the user interface.
        QtWidgets.QMainWindow.__init__(self)

        # Window configuration
        self.setWindowTitle("AUTOLAB - Control Panel")
        self.setWindowIcon(QtGui.QIcon(icons['autolab']))
        self.setFocus()
        self.activateWindow()
        self.resize(700, 573)

        # Main frame configuration: centralWidget(verticalLayout(splitter(tree)))

        # Tree widget configuration
        class MyQTreeWidget(QtWidgets.QTreeWidget):

            def __init__(self, gui, parent=None):
                self.gui = gui
                QtWidgets.QTreeWidget.__init__(self, parent)

            def startDrag(self, event):

                if self.gui.scanner is not None:
                    self.gui.scanner.setWindowState(
                        self.gui.scanner.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                    self.gui.scanner.activateWindow()
                QtWidgets.QTreeWidget.startDrag(self, event)

        self.tree = MyQTreeWidget(self)
        self.tree.last_drag = None
        self.tree.setHeaderLabels(['Objects', 'Type', 'Actions', 'Values', ''])
        self.tree.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.tree.header().setMinimumSectionSize(15)
        self.tree.header().resizeSection(0, 200)
        self.tree.header().resizeSection(4, 15)
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.tree.header().setStretchLastSection(False)
        self.tree.itemClicked.connect(self.itemClicked)
        self.tree.itemPressed.connect(self.itemPressed)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.rightClick)
        self.tree.setAlternatingRowColors(True)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.tree)

        verticalLayout = QtWidgets.QVBoxLayout()
        verticalLayout.setSpacing(0)
        verticalLayout.setContentsMargins(0,0,0,0)
        verticalLayout.addWidget(self.splitter)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(verticalLayout)
        self.setCentralWidget(centralWidget)

        self.menuBar = self.menuBar()
        self.statusBar = self.statusBar()

        # Thread manager
        self.threadManager = ThreadManager(self)

        # Scanner / Monitors
        self.scanner = None
        self.plotter = None
        self.monitors = {}
        self.sliders = {}
        self.threadDeviceDict = {}
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
        autolabConfig.setIcon(QtGui.QIcon(icons['config']))
        autolabConfig.triggered.connect(self.openAutolabConfig)
        autolabConfig.setStatusTip("Open the Autolab configuration file")

        plotterConfig = settingsMenu.addAction('Plotter config')
        plotterConfig.setIcon(QtGui.QIcon(icons['config']))
        plotterConfig.triggered.connect(self.openPlotterConfig)
        plotterConfig.setStatusTip("Open the plotter configuration file")

        settingsMenu.addSeparator()

        devicesConfig = settingsMenu.addAction('Devices config')
        devicesConfig.setIcon(QtGui.QIcon(icons['config']))
        devicesConfig.triggered.connect(self.openDevicesConfig)
        devicesConfig.setStatusTip("Open the devices configuration file")

        refreshAction = settingsMenu.addAction('Refresh devices')
        refreshAction.triggered.connect(self.initialize)
        refreshAction.setStatusTip('Reload devices setting')

        # Help menu
        helpMenu = self.menuBar.addMenu('Help')

        reportAction = helpMenu.addAction('Report bugs / suggestions')
        reportAction.setIcon(QtGui.QIcon(icons['github']))
        reportAction.triggered.connect(web.report)
        reportAction.setStatusTip('Open the issue webpage of this project on GitHub')

        helpMenu.addSeparator()

        helpAction = helpMenu.addAction('Documentation')
        helpAction.setIcon(QtGui.QIcon(icons['readthedocs']))
        helpAction.triggered.connect(lambda: web.doc('default'))
        helpAction.setStatusTip('Open the documentation on Read The Docs website')

        helpActionOffline = helpMenu.addAction('Documentation (Offline)')
        helpActionOffline.setIcon(QtGui.QIcon(icons['pdf']))
        helpActionOffline.triggered.connect(lambda: web.doc(False))
        helpActionOffline.setStatusTip('Open the pdf documentation form local file')

        # Timer for device instantiation
        self.timerDevice = QtCore.QTimer(self)
        self.timerDevice.setInterval(50) # ms
        self.timerDevice.timeout.connect(self.timerAction)

        # queue and timer to add/remove plot from driver
        self.queue_driver = queue.Queue()
        self.dict_widget = {}
        self.timerQueue = QtCore.QTimer(self)
        self.timerQueue.setInterval(int(50)) # ms
        self.timerQueue.timeout.connect(self._queueDriverHandler)
        self.timerQueue.start()  # OPTIMIZE: should be started only when needed but difficult to know it before openning device which occurs in a diff thread! (can't start timer on diff thread)

        # Import Autolab config
        control_center_config = config.get_control_center_config()
        logger_active = utilities.boolean(control_center_config['logger'])
        console_active = utilities.boolean(control_center_config['console'])
        print_active = utilities.boolean(control_center_config['print'])

        # Prepare docker
        if console_active or logger_active:
            from pyqtgraph.dockarea.DockArea import DockArea
            from pyqtgraph.dockarea.Dock import Dock

        # Set logger
        self.stdout = OutputWrapper(self, True, logger_active, print_active)
        self.stderr = OutputWrapper(self, False, logger_active, print_active)

        if logger_active:
            area_1 = DockArea(self)
            self.splitter.addWidget(area_1)

            logger_dock = Dock("Logger")
            area_1.addDock(logger_dock, 'bottom')
            self._logger_dock = logger_dock

            self.logger = QtWidgets.QTextBrowser(self)
            self.loggerDefaultColor = self.logger.textColor()
            self.stdout.outputWritten.connect(self.handleOutput)
            self.stderr.outputWritten.connect(self.handleOutput)

            logger_dock.addWidget(self.logger)

        if console_active:
            from pyqtgraph.console import ConsoleWidget
            import autolab  # OPTIMIZE: not good to import autolab?
            namespace = {'np': np, 'pd': pd, 'autolab': autolab}
            text = """ Packages imported: autolab, numpy as np, pandas as pd.\n"""
            area_2 = DockArea(self)
            self.splitter.addWidget(area_2)

            console_dock = Dock("Console")
            self._console_dock = console_dock
            area_2.addDock(console_dock, 'bottom')

            console_widget = ConsoleWidget(namespace=namespace, text=text)
            console_dock.addWidget(console_widget)

    def createWidget(self, widget: Type, *args, **kwargs):
        """ Function used by a driver to add a widget.
        Mainly used to open a figure outside the GUI from a driver. """
        unique_name = str(uuid.uuid4())
        self.queue_driver.put(('create', unique_name, widget, args, kwargs))

        start = time.time()
        while True:
            widget_created = self.dict_widget.get(unique_name)

            if widget_created: return widget_created
            time.sleep(0.01)
            if (time.time() - start) > 1:
                print(f"Warning: Importation of {widget} too long, skip it",
                      file=sys.stderr)
                return None

    def removeWidget(self, widget: Type):
        """ Function used by a driver to remove a widget record from GUI """
        self.queue_driver.put(('remove', "", widget, (), {}))

    def _queueDriverHandler(self):
        """ Adds/Removes plot from a driver requests throught a queue """
        while not self.queue_driver.empty():
            data = self.queue_driver.get()
            action = data[0]
            widget_name = data[1]
            widget = data[2]
            args = data[3]
            kwargs = data[4]

            if action == 'create':
                widget = widget(*args, **kwargs)
                self.dict_widget[widget_name] = widget
            elif action == "remove":
                d = self.dict_widget
                if widget is not None:
                    widget_pos = list(d.values()).index(widget)
                    if widget_pos is not None:
                        widget_name = list(d.keys())[widget_pos]
                        widget = d.get(widget_name)
                        if widget is not None: d.pop(widget_name)

    def handleOutput(self, text: str, stdout: bool):
        if not stdout: self.logger.setTextColor(QtCore.Qt.red)
        self.logger.insertPlainText(text)
        self.logger.moveCursor(QtGui.QTextCursor.End)
        self.logger.setTextColor(self.loggerDefaultColor)

    def timerAction(self):
        """ This function checks if a module has been loaded and put to the queue.
        If it has been, associate item and module """
        threadItemDictTemp = self.threadItemDict.copy()
        threadDeviceDictTemp = self.threadDeviceDict.copy()

        for item_id in threadDeviceDictTemp.keys():
            item = threadItemDictTemp[item_id]
            module = threadDeviceDictTemp[item_id]

            self.associate(item, module)
            item.setExpanded(True)

            # if hasattr(module.instance, 'gui'):  # Can't just start timer here because driver created before. But could reduce timer interval here if want to start with longer interval while no driver openned
            #     self.timerQueue.setInterval(int(50)) # ms

            self.threadItemDict.pop(item_id)
            self.threadDeviceDict.pop(item_id)

        if len(threadItemDictTemp) == 0:
            self.timerDevice.stop()

    def initialize(self):
        """ This function will create the first items in the tree, but will
        associate only the ones already loaded in autolab """
        self.tree.clear()
        for devName in devices.list_devices():
            item = TreeWidgetItemModule(self.tree, devName, self)

            for i in range(5):
                item.setBackground(i, QtGui.QColor('#9EB7F5'))  # blue

            if devName in devices.list_loaded_devices(): self.itemClicked(item)

    def setStatus(self, message: str, timeout: int = 0, stdout: bool = True):
        """ Modify the message displayed in the status bar and add error message to logger """
        self.statusBar.showMessage(message, timeout)
        if not stdout: print(message, file=sys.stderr)

    def clearStatus(self):
        """ Erase the message displayed in the status bar """
        self.setStatus('')

    def rightClick(self, position: QtCore.QPoint):
        """ Function called when a right click has been detected in the tree """
        item = self.tree.itemAt(position)
        if hasattr(item, 'menu'): item.menu(position)

    def itemClicked(self, item: QtWidgets.QTreeWidgetItem):
        """ Function called when a normal click has been detected in the tree.
            Check the association if it is a main item """
        if (item.parent() is None and not item.loaded
                and id(item) not in self.threadItemDict.keys()):
            self.threadItemDict[id(item)] = item  # needed before start of timer to avoid bad timing and to stop thread before loading is done
            self.threadManager.start(item, 'load')  # load device and add it to queue for timer to associate it later (doesn't block gui while device is openning)
            self.timerDevice.start()

    def itemPressed(self, item: QtWidgets.QTreeWidgetItem):
        """ Function called when a click (not released) has been detected in the tree.
            Store last dragged variable in tree so scanner can know it when it is dropped there.
            """
        if hasattr(item, "module"):
            if item.is_not_submodule: self.tree.last_drag = item.name
            else: self.tree.last_drag = None
        elif hasattr(item, "variable"): self.tree.last_drag = item.variable
        elif hasattr(item, "action"): self.tree.last_drag = item.action
        else: self.tree.last_drag = None

    def associate(self, item: QtWidgets.QTreeWidgetItem, module: devices.Device):
        """ Function called to associate a main module to one item in the tree """
        # load the entire module (submodules, variables, actions)
        item.load(module)

        read_init_list = module._read_init_list
        for mod in module._mod.values():
            read_init_list.extend(mod._read_init_list)
        for variable in read_init_list:
            try:
                variable()
            except:
                self.setStatus(f"Can't read variable {variable.address()} on instantiation",
                               10000, False)

    def openScanner(self):
        """ This function open the scanner associated to this variable. """
        # If the scanner is not already running, create one
        if self.scanner is None:
            self.scanner = Scanner(self)
            self.scanner.show()
            self.scanner.activateWindow()
            self.activateWindow() # Put main window back to the front
        # If the scanner is already running, just make as the front window
        else:
            self.scanner.setWindowState(
                self.scanner.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.scanner.activateWindow()

    def openPlotter(self):
        """ This function open the plotter associated to this variable. """
        # If the plotter is not already running, create one
        if self.plotter is None:
            self.plotter = Plotter(self)
        # If the plotter is not active open it (keep data if closed)
        if not self.plotter.active:
            self.plotter.show()
            self.plotter.activateWindow()
            self.plotter.active = True
        # If the plotter is already running, just make as the front window
        else:
            self.plotter.setWindowState(
                self.plotter.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.plotter.activateWindow()

    @staticmethod
    def openAutolabConfig():
        """ Open the Autolab configuration file """
        utilities.openFile(paths.AUTOLAB_CONFIG)

    @staticmethod
    def openDevicesConfig():
        """ Open the devices configuration file """
        utilities.openFile(paths.DEVICES_CONFIG)

    @staticmethod
    def openPlotterConfig():
        """ Open the plotter configuration file """
        utilities.openFile(paths.PLOTTER_CONFIG)

    def setScanParameter(self, recipe_name: str, param_name: str,
                         variable: devices.Device):
        """ Set the selected variable has parameter for the recipe """
        if self.scanner is None:
            self.openScanner()

        self.scanner.configManager.setParameter(recipe_name, param_name, variable)

    def addStepToScanRecipe(self, recipe_name: str, stepType: str,
                            element: devices.Device):
        """ Add the selected variable has a step for the recipe """
        if self.scanner is None:
            self.openScanner()

        self.scanner.configManager.addRecipeStep(recipe_name, stepType, element)

    def getRecipeName(self) -> str:
        """ Returns the name of the recipe that will receive the variables
        from the control center """
        if self.scanner is None:
            self.openScanner()

        return self.scanner.selectRecipe_comboBox.currentText()

    def getParameterName(self) -> str:
        """ Returns the name of the parameter that will receive the variables
        from the control center """
        if self.scanner is None:
            self.openScanner()

        return self.scanner.selectParameter_comboBox.currentText()

    def clearScanner(self):
        """ This clear the scanner instance reference when quitted """
        self.scanner = None

    def clearPlotter(self):
        """ This deactivate the plotter when quitted but keep the instance in memory """
        if self.plotter is not None:
            self.plotter.active = False  # don't want to close plotter because want to keep data

    def closeEvent(self, event):
        """ This function does some steps before the window is really killed """
        if self.scanner is not None:
            self.scanner.close()

        if self.plotter is not None:
            self.plotter.figureManager.fig.deleteLater()
            for children in self.plotter.findChildren(
                    QtWidgets.QWidget, options=QtCore.Qt.FindDirectChildrenOnly):
                children.deleteLater()

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

        if hasattr(self, '_logger_dock'): self._logger_dock.deleteLater()
        if hasattr(self, '_console_dock'): self._console_dock.deleteLater()

        try:
            import pyqtgraph as pg
            # Prevent 'RuntimeError: wrapped C/C++ object of type ViewBox has been deleted' when reloading gui
            for view in pg.ViewBox.AllViews.copy().keys():
                pg.ViewBox.forgetView(id(view), view)

            pg.ViewBox.quit()
        except: pass

        self.timerDevice.stop()
        self.timerQueue.stop()

        for children in self.findChildren(
                QtWidgets.QWidget, options=QtCore.Qt.FindDirectChildrenOnly):
            children.deleteLater()

        super().closeEvent(event)

        VARIABLES.clear()  # reset variables defined in the GUI
