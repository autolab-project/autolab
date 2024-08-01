# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 23:29:33 2017

@author: Quentin Chateiller
quentin.chateiller@c2n.upsaclay.fr

"""

import platform
import sys
import queue
import time
import uuid
from typing import Any, Type, Union

import numpy as np
import pandas as pd
import qtpy
from qtpy import QtCore, QtWidgets, QtGui
import pyqtgraph as pg

from .thread import ThreadManager
from .treewidgets import TreeWidgetItemModule
from ..scanning.main import Scanner
from ..plotting.main import Plotter
from ..GUI_utilities import get_font_size
from ..icons import icons
from ...paths import PATHS
from ...devices import (list_devices, list_loaded_devices, Device, close,
                        get_final_device_config)
from ...elements import Variable as Variable_og
from ...elements import Action
from ...drivers import (list_drivers, load_driver_lib, get_connection_names,
                        get_driver_class, get_connection_class, get_class_args)
from ...config import (get_control_center_config, get_all_devices_configs,
                       save_config)
from ...utilities import boolean, open_file
from ...variables import VARIABLES
from ...repository import _install_drivers_custom
from ...web import project_url, drivers_url, doc_url, report, doc
from .... import __version__


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
        super().__init__()

        # Window configuration
        self.setWindowTitle("AUTOLAB - Control Panel")
        self.setWindowIcon(QtGui.QIcon(icons['autolab']))
        self.setFocus()
        self.activateWindow()
        self.resize(700, 573)

        self.close_device_on_exit = True

        # Main frame configuration: centralWidget(verticalLayout(splitter(tree)))

        # Tree widget configuration
        class MyQTreeWidget(QtWidgets.QTreeWidget):

            def __init__(self, gui, parent=None):
                self.gui = gui
                super().__init__(parent)

            def startDrag(self, event):

                if self.gui.scanner is not None:
                    self.gui.scanner.setWindowState(
                        self.gui.scanner.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                    self.gui.scanner.activateWindow()
                QtWidgets.QTreeWidget.startDrag(self, event)

            def keyPressEvent(self, event):
                if (event.key() == QtCore.Qt.Key_C
                        and event.modifiers() == QtCore.Qt.ControlModifier):
                    self.copy_item(event)
                else:
                    super().keyPressEvent(event)

            def copy_item(self, event):
                if len(self.selectedItems()) == 0:
                    super().keyPressEvent(event)
                    return None
                item = self.selectedItems()[0]  # assume can select only one item
                if hasattr(item, 'variable'):
                    text = item.variable.address()
                elif hasattr(item, 'action'):
                    text = item.action.address()
                elif hasattr(item, 'module'):
                    if hasattr(item.module, 'address'):
                        text = item.module.address()
                    else:
                        text = item.name
                else:
                    print(f'Should not be possible: {item}')
                    super().keyPressEvent(event)
                    return None

                # Copy the text to the system clipboard
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(text)

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

        closeWidget = QtWidgets.QCheckBox('Close device connection on exit')
        closeWidget.setChecked(self.close_device_on_exit)
        closeWidget.stateChanged.connect(
            lambda state: setattr(self, 'close_device_on_exit', state))

        verticalLayout.addWidget(closeWidget)

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
        self.about = None
        self.addDevice = None
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

        addDeviceAction = settingsMenu.addAction('Add device')
        addDeviceAction.setIcon(QtGui.QIcon(icons['add']))
        addDeviceAction.triggered.connect(lambda: self.openAddDevice())
        addDeviceAction.setStatusTip("Open the utility to add a device")

        downloadDriverAction = settingsMenu.addAction('Download drivers')
        downloadDriverAction.setIcon(QtGui.QIcon(icons['add']))
        downloadDriverAction.triggered.connect(self.downloadDriver)
        downloadDriverAction.setStatusTip("Open the utility to download drivers")

        refreshAction = settingsMenu.addAction('Refresh devices')
        refreshAction.triggered.connect(self.initialize)
        refreshAction.setStatusTip('Reload devices setting')

        # Help menu
        helpMenu = self.menuBar.addMenu('Help')

        reportAction = helpMenu.addAction('Report bugs / suggestions')
        reportAction.setIcon(QtGui.QIcon(icons['github']))
        reportAction.triggered.connect(report)
        reportAction.setStatusTip('Open the issue webpage of this project on GitHub')

        helpMenu.addSeparator()

        helpAction = helpMenu.addAction('Documentation')
        helpAction.setIcon(QtGui.QIcon(icons['readthedocs']))
        helpAction.triggered.connect(lambda: doc('default'))
        helpAction.setStatusTip('Open the documentation on Read The Docs website')

        helpActionOffline = helpMenu.addAction('Documentation (Offline)')
        helpActionOffline.setIcon(QtGui.QIcon(icons['pdf']))
        helpActionOffline.triggered.connect(lambda: doc(False))
        helpActionOffline.setStatusTip('Open the pdf documentation form local file')

        helpMenu.addSeparator()

        aboutAction = helpMenu.addAction('About Autolab')
        aboutAction.setIcon(QtGui.QIcon(icons['autolab']))
        aboutAction.triggered.connect(self.openAbout)
        aboutAction.setStatusTip('Information about Autolab')

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
        control_center_config = get_control_center_config()
        logger_active = boolean(control_center_config['logger'])
        console_active = boolean(control_center_config['console'])
        print_active = boolean(control_center_config['print'])

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
                        widget_name = list(d)[widget_pos]
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

        for item_id, module in threadDeviceDictTemp.items():
            item = threadItemDictTemp[item_id]

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
        try:
            devices_name = list_devices()
        except Exception as e:
            self.setStatus(f'Error {e}', 10000, False)
        else:
            for dev_name in devices_name:
                item = TreeWidgetItemModule(self.tree, dev_name, self)

                for i in range(5):
                    item.setBackground(i, QtGui.QColor('#9EB7F5'))  # blue

                if dev_name in list_loaded_devices(): self.itemClicked(item)

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
        elif item is None: self.addDeviceMenu(position)

    def addDeviceMenu(self, position: QtCore.QPoint):
        """ Open menu to ask if want to add new device """
        menu = QtWidgets.QMenu()
        addDeviceChoice = menu.addAction('Add device')
        addDeviceChoice.setIcon(QtGui.QIcon(icons['add']))

        choice = menu.exec_(self.tree.viewport().mapToGlobal(position))

        if choice == addDeviceChoice:
            self.openAddDevice()

    def itemClicked(self, item: QtWidgets.QTreeWidgetItem):
        """ Function called when a normal click has been detected in the tree.
            Check the association if it is a main item """
        if (item.parent() is None and not item.loaded
                and id(item) not in self.threadItemDict):
            self.threadItemDict[id(item)] = item  # needed before start of timer to avoid bad timing and to stop thread before loading is done
            self.threadManager.start(item, 'load')  # load device and add it to queue for timer to associate it later (doesn't block gui while device is openning)
            self.timerDevice.start()

    def itemCanceled(self, item):
        """ Cancel the device openning. Can be used to avoid GUI blocking
        for devices with infinite loading issue """
        if id(item) in self.threadManager.threads_conn:
            tid = self.threadManager.threads_conn[id(item)]
            self.threadManager.threads[tid].endSignal.emit(
                f'Cancel loading device {item.name}')
            self.threadManager.threads[tid].terminate()

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

    def associate(self, item: QtWidgets.QTreeWidgetItem, module: Device):
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
        """ This function open the scanner. """
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
        """ This function open the plotter. """
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

    def openAbout(self):
        """ This function open the about window. """
        # If the about window is not already running, create one
        if self.about is None:
            self.about = AboutWindow(self)
            self.about.show()
            self.about.activateWindow()
        # If the about window is already running, just make as the front window
        else:
            self.about.setWindowState(
                self.about.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.about.activateWindow()

    def openAddDevice(self, item: QtWidgets.QTreeWidgetItem = None):
        """ This function open the add device window. """
        # If the add device window is not already running, create one
        if self.addDevice is None:
            self.addDevice = addDeviceWindow(self)
            self.addDevice.show()
            self.addDevice.activateWindow()
        # If the add device window is already running, just make as the front window
        else:
            self.addDevice.setWindowState(
                self.addDevice.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.addDevice.activateWindow()

        # Modify existing device
        if item is not None:
            name = item.name
            try:
                conf = get_final_device_config(item.name)
            except Exception as e:
                self.setStatus(str(e), 10000, False)
            else:
                self.addDevice.modify(name, conf)

    def downloadDriver(self):
        """ This function open the download driver window. """
        _install_drivers_custom(parent=self)

    @staticmethod
    def openAutolabConfig():
        """ Open the Autolab configuration file """
        open_file(PATHS['autolab_config'])

    @staticmethod
    def openDevicesConfig():
        """ Open the devices configuration file """
        open_file(PATHS['devices_config'])

    @staticmethod
    def openPlotterConfig():
        """ Open the plotter configuration file """
        open_file(PATHS['plotter_config'])

    def setScanParameter(self, recipe_name: str, param_name: str,
                         variable: Variable_og):
        """ Set the selected variable has parameter for the recipe """
        if self.scanner is None:
            self.openScanner()

        self.scanner.configManager.setParameter(recipe_name, param_name, variable)

    def addStepToScanRecipe(self, recipe_name: str, stepType: str,
                            element: Union[Variable_og, Action]):
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

    def clearAbout(self):
        """ This clear the about instance reference when quitted """
        self.about = None

    def clearAddDevice(self):
        """ This clear the addDevice instance reference when quitted """
        self.addDevice = None

    def closeEvent(self, event):
        """ This function does some steps before the window is really killed """
        if self.scanner is not None:
            self.scanner.close()

        if self.plotter is not None:
            self.plotter.figureManager.fig.deleteLater()
            for children in self.plotter.findChildren(QtWidgets.QWidget):
                children.deleteLater()

            self.plotter.close()

        if self.about is not None:
            self.about.close()

        if self.addDevice is not None:
            self.addDevice.close()

        monitors = list(self.monitors.values())
        for monitor in monitors:
            monitor.close()

        for slider in list(self.sliders.values()):
            slider.close()

        if self.close_device_on_exit:
            close()  # close all devices

        QtWidgets.QApplication.quit()  # close the control center interface

        if hasattr(self, 'stdout'):
            sys.stdout = self.stdout._stream
            sys.stderr = self.stderr._stream

        if hasattr(self, '_logger_dock'): self._logger_dock.deleteLater()
        if hasattr(self, '_console_dock'): self._console_dock.deleteLater()

        try:
            # Prevent 'RuntimeError: wrapped C/C++ object of type ViewBox has been deleted' when reloading gui
            for view in pg.ViewBox.AllViews.copy().keys():
                pg.ViewBox.forgetView(id(view), view)

            pg.ViewBox.quit()
        except: pass

        self.timerDevice.stop()
        self.timerQueue.stop()

        for children in self.findChildren(QtWidgets.QWidget):
            children.deleteLater()

        super().closeEvent(event)

        VARIABLES.clear()  # reset variables defined in the GUI


class addDeviceWindow(QtWidgets.QMainWindow):

    def __init__(self, parent: QtWidgets.QMainWindow = None):

        super().__init__(parent)
        self.mainGui = parent
        self.setWindowTitle('Autolab - Add device')
        self.setWindowIcon(QtGui.QIcon(icons['autolab']))

        self.statusBar = self.statusBar()

        self._prev_name = ''
        self._prev_conn = ''

        try:
            import pyvisa as visa
            self.rm = visa.ResourceManager()
        except:
            self.rm = None

        self._font_size = get_font_size() + 1

        # Main layout creation
        layoutWindow = QtWidgets.QVBoxLayout()
        layoutWindow.setAlignment(QtCore.Qt.AlignTop)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(layoutWindow)
        self.setCentralWidget(centralWidget)

        # Device nickname
        layoutDeviceNickname = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(layoutDeviceNickname)

        label = QtWidgets.QLabel('Device')
        label.setMinimumSize(60, 23)
        label.setMaximumSize(60, 23)

        self.deviceNickname = QtWidgets.QLineEdit()
        self.deviceNickname.setText('my_device')

        layoutDeviceNickname.addWidget(label)
        layoutDeviceNickname.addWidget(self.deviceNickname)

        # Driver name
        layoutDriverName = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(layoutDriverName)

        label = QtWidgets.QLabel('Driver')
        label.setMinimumSize(60, 23)
        label.setMaximumSize(60, 23)

        self.driversComboBox = QtWidgets.QComboBox()
        self.driversComboBox.addItems(list_drivers())
        self.driversComboBox.activated.connect(self.driverChanged)

        layoutDriverName.addWidget(label)
        layoutDriverName.addWidget(self.driversComboBox)

        # Driver connection
        layoutDriverConnection = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(layoutDriverConnection)

        label = QtWidgets.QLabel('Connection')
        label.setMinimumSize(60, 23)
        label.setMaximumSize(60, 23)

        self.connectionComboBox = QtWidgets.QComboBox()
        self.connectionComboBox.activated.connect(self.connectionChanged)

        layoutDriverConnection.addWidget(label)
        layoutDriverConnection.addWidget(self.connectionComboBox)

        # Driver arguments
        self.layoutDriverArgs = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(self.layoutDriverArgs)

        self.layoutDriverOtherArgs = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(self.layoutDriverOtherArgs)

        # layout for optional args
        self.layoutOptionalArg = QtWidgets.QVBoxLayout()
        layoutWindow.addLayout(self.layoutOptionalArg)

        # Add argument
        layoutButtonArg = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(layoutButtonArg)

        addOptionalArg = QtWidgets.QPushButton('Add argument')
        addOptionalArg.setMinimumSize(0, 23)
        addOptionalArg.setMaximumSize(100, 23)
        addOptionalArg.setIcon(QtGui.QIcon(icons['add']))
        addOptionalArg.clicked.connect(lambda state: self.addOptionalArgClicked())

        layoutButtonArg.addWidget(addOptionalArg)
        layoutButtonArg.setAlignment(QtCore.Qt.AlignLeft)

        # Add device
        layoutButton = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(layoutButton)

        self.addButton = QtWidgets.QPushButton('Add device')
        self.addButton.clicked.connect(self.addButtonClicked)

        layoutButton.addWidget(self.addButton)

        # update driver name combobox
        self.driverChanged()

    def addOptionalArgClicked(self, key: str = None, val: str = None):
        """ Add new layout for optional argument """
        layout = QtWidgets.QHBoxLayout()
        self.layoutOptionalArg.addLayout(layout)

        widget = QtWidgets.QLineEdit()
        widget.setText(key)
        layout.addWidget(widget)
        widget = QtWidgets.QLineEdit()
        widget.setText(val)
        layout.addWidget(widget)
        widget = QtWidgets.QPushButton()
        widget.setIcon(QtGui.QIcon(icons['remove']))
        widget.clicked.connect(lambda: self.removeOptionalArgClicked(layout))
        layout.addWidget(widget)

    def removeOptionalArgClicked(self, layout):
        """ Remove optional argument layout """
        for j in reversed(range(layout.count())):
            layout.itemAt(j).widget().setParent(None)
        layout.setParent(None)

    def addButtonClicked(self):
        """ Add the device to the config file """
        device_name = self.deviceNickname.text()
        driver_name = self.driversComboBox.currentText()
        conn = self.connectionComboBox.currentText()

        if device_name == '':
            self.setStatus('Need device name', 10000, False)
            return None

        device_dict = {}
        device_dict['driver'] = driver_name
        device_dict['connection'] = conn

        for layout in (self.layoutDriverArgs, self.layoutDriverOtherArgs):
            for i in range(0, (layout.count()//2)*2, 2):
                key = layout.itemAt(i).widget().text()
                val = layout.itemAt(i+1).widget().text()
                device_dict[key] = val

        for i in range(self.layoutOptionalArg.count()):
            layout = self.layoutOptionalArg.itemAt(i).layout()
            key = layout.itemAt(0).widget().text()
            val = layout.itemAt(1).widget().text()
            device_dict[key] = val

        # Update devices config
        device_config = get_all_devices_configs()
        new_device = {device_name: device_dict}
        device_config.update(new_device)
        save_config('devices_config', device_config)

        if hasattr(self.mainGui, 'initialize'): self.mainGui.initialize()

        self.close()

    def modify(self, nickname: str, conf: dict):
        """ Modify existing driver (not optimized) """

        self.setWindowTitle('Autolab - Modify device')
        self.addButton.setText('Modify device')

        self.deviceNickname.setText(nickname)
        self.deviceNickname.setEnabled(False)
        driver_name = conf.pop('driver')
        conn = conf.pop('connection')
        index = self.driversComboBox.findText(driver_name)
        self.driversComboBox.setCurrentIndex(index)
        self.driverChanged()

        try:
            driver_lib = load_driver_lib(driver_name)
        except: pass
        else:
            list_conn = get_connection_names(driver_lib)
            if conn not in list_conn:
                if list_conn:
                    self.setStatus(f"Connection {conn} not found, switch to {list_conn[0]}", 10000, False)
                    conn = list_conn[0]
                else:
                    self.setStatus(f"No connections available for driver '{driver_name}'", 10000, False)
                    conn =  ''

        index = self.connectionComboBox.findText(conn)
        self.connectionComboBox.setCurrentIndex(index)
        self.connectionChanged()

        # Used to remove default value
        try:
            driver_lib = load_driver_lib(driver_name)
            driver_class = get_driver_class(driver_lib)
            assert hasattr(driver_class, 'slot_config')
        except:
            slot_config = '<MODULE_NAME>'
        else:
            slot_config = f'{driver_class.slot_config}'

        # Update args
        for layout in (self.layoutDriverArgs, self.layoutDriverOtherArgs):
            for i in range(0, (layout.count()//2)*2, 2):
                key = layout.itemAt(i).widget().text()
                if key in conf:
                    layout.itemAt(i+1).widget().setText(conf[key])
                    conf.pop(key)

        # Update optional args
        for i in reversed(range(self.layoutOptionalArg.count())):
            layout = self.layoutOptionalArg.itemAt(i).layout()
            key = layout.itemAt(0).widget().text()
            val_tmp = layout.itemAt(1).widget().text()
            # Remove default value
            if ((key == 'slot1' and val_tmp == slot_config)
                    or (key == 'slot1_name' and val_tmp == 'my_<MODULE_NAME>')):
                for j in reversed(range(layout.count())):
                    layout.itemAt(j).widget().setParent(None)
                layout.setParent(None)
            elif key in conf:
                layout.itemAt(1).widget().setText(conf[key])
                conf.pop(key)

        # Add remaining optional args from config
        for key, val in conf.items():
            self.addOptionalArgClicked(key, val)

    def driverChanged(self):
        """ Update driver information """
        driver_name = self.driversComboBox.currentText()

        if driver_name == self._prev_name: return None
        self._prev_name = driver_name

        try:
            driver_lib = load_driver_lib(driver_name)
        except Exception as e:
            # If error with driver remove all layouts
            self.setStatus(f"Can't load {driver_name}: {e}", 10000, False)

            self.connectionComboBox.clear()

            for layout in (self.layoutDriverArgs, self.layoutDriverOtherArgs):
                for i in reversed(range(layout.count())):
                    layout.itemAt(i).widget().setParent(None)

            for i in reversed(range(self.layoutOptionalArg.count())):
                layout = self.layoutOptionalArg.itemAt(i).layout()
                for j in reversed(range(layout.count())):
                    layout.itemAt(j).widget().setParent(None)
                layout.setParent(None)

            return None

        self.setStatus('')

        # Update available connections
        connections = get_connection_names(driver_lib)
        self.connectionComboBox.clear()
        self.connectionComboBox.addItems(connections)

        # update selected connection information
        self._prev_conn = ''
        self.connectionChanged()

        # reset layoutDriverOtherArgs
        for i in reversed(range(self.layoutDriverOtherArgs.count())):
            self.layoutDriverOtherArgs.itemAt(i).widget().setParent(None)

        # used to skip doublon key
        conn = self.connectionComboBox.currentText()
        try:
            driver_instance = get_connection_class(driver_lib, conn)
        except:
            connection_args = {}
        else:
            connection_args = get_class_args(driver_instance)

        # populate layoutDriverOtherArgs
        driver_class = get_driver_class(driver_lib)
        other_args = get_class_args(driver_class)
        for key, val in other_args.items():
            if key in connection_args: continue
            widget = QtWidgets.QLabel()
            widget.setText(key)
            self.layoutDriverOtherArgs.addWidget(widget)
            widget = QtWidgets.QLineEdit()
            widget.setText(str(val))
            self.layoutDriverOtherArgs.addWidget(widget)

        # reset layoutOptionalArg
        for i in reversed(range(self.layoutOptionalArg.count())):
            layout = self.layoutOptionalArg.itemAt(i).layout()
            for j in reversed(range(layout.count())):
                layout.itemAt(j).widget().setParent(None)
            layout.setParent(None)

        # populate layoutOptionalArg
        if hasattr(driver_class, 'slot_config'):
            self.addOptionalArgClicked('slot1', f'{driver_class.slot_config}')
            self.addOptionalArgClicked('slot1_name', 'my_<MODULE_NAME>')

    def connectionChanged(self):
        """ Update connection information """
        conn = self.connectionComboBox.currentText()

        if conn == self._prev_conn: return None
        self._prev_conn = conn

        driver_name = self.driversComboBox.currentText()
        driver_lib = load_driver_lib(driver_name)

        connection_args = get_class_args(
            get_connection_class(driver_lib, conn))

        # reset layoutDriverArgs
        for i in reversed(range(self.layoutDriverArgs.count())):
            self.layoutDriverArgs.itemAt(i).widget().setParent(None)

        conn_widget = None
        # populate layoutDriverArgs
        for key, val in connection_args.items():
            widget = QtWidgets.QLabel()
            widget.setText(key)
            self.layoutDriverArgs.addWidget(widget)

            widget = QtWidgets.QLineEdit()
            widget.setText(str(val))
            self.layoutDriverArgs.addWidget(widget)

            if key == 'address':
                conn_widget = widget

        if self.rm is not None and conn == 'VISA':
            widget = QtWidgets.QComboBox()
            widget.clear()
            conn_list = ('Available connections',) + tuple(self.rm.list_resources())
            widget.addItems(conn_list)
            if conn_widget is not None:
                widget.activated.connect(
                    lambda item, conn_widget=conn_widget: conn_widget.setText(
                        widget.currentText()) if widget.currentText(
                            ) != 'Available connections' else conn_widget.text())
            self.layoutDriverArgs.addWidget(widget)

    def setStatus(self, message: str, timeout: int = 0, stdout: bool = True):
        """ Modify the message displayed in the status bar and add error message to logger """
        self.statusBar.showMessage(message, timeout)
        if not stdout: print(message, file=sys.stderr)

    def closeEvent(self, event):
        """ Does some steps before the window is really killed """
        # Delete reference of this window in the control center
        if hasattr(self.mainGui, 'clearAddDevice'): self.mainGui.clearAddDevice()

        if self.mainGui is None:
            QtWidgets.QApplication.quit()  # close the monitor app


class AboutWindow(QtWidgets.QMainWindow):

    def __init__(self, parent: QtWidgets.QMainWindow = None):

        super().__init__(parent)
        self.mainGui = parent
        self.setWindowTitle('Autolab - About')
        self.setWindowIcon(QtGui.QIcon(icons['autolab']))

        versions = get_versions()

        # Main layout creation
        layoutWindow = QtWidgets.QVBoxLayout()
        layoutTab = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(layoutTab)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(layoutWindow)
        self.setCentralWidget(centralWidget)

        frameOverview = QtWidgets.QFrame()
        layoutOverview = QtWidgets.QVBoxLayout(frameOverview)

        frameLegal = QtWidgets.QFrame()
        layoutLegal = QtWidgets.QVBoxLayout(frameLegal)

        tab = QtWidgets.QTabWidget(self)
        tab.addTab(frameOverview, 'Overview')
        tab.addTab(frameLegal, 'Legal')

        label_pic = QtWidgets.QLabel()
        label_pic.setPixmap(QtGui.QPixmap(icons['autolab']))

        label_autolab = QtWidgets.QLabel(f"<h2>Autolab {versions['autolab']}</h2>")
        label_autolab.setAlignment(QtCore.Qt.AlignCenter)

        frameIcon = QtWidgets.QFrame()
        layoutIcon = QtWidgets.QVBoxLayout(frameIcon)
        layoutIcon.addWidget(label_pic)
        layoutIcon.addWidget(label_autolab)
        layoutIcon.addStretch()

        layoutTab.addWidget(frameIcon)
        layoutTab.addWidget(tab)

        label_versions = QtWidgets.QLabel(
            f"""
            <h1>Autolab</h1>

            <h3>Python package for scientific experiments automation</h3>

            <p>
            {versions['system']} {versions['release']}
            <br>
            Python {versions['python']} - {versions['bitness']}-bit
            <br>
            {versions['qt_api']} {versions['qt_api_ver']} |
            PyQtGraph {versions['pyqtgraph']} |
            Numpy {versions['numpy']} |
            Pandas {versions['pandas']}
            </p>

            <p>
            <a href="{project_url}">Project</a> |
            <a href="{drivers_url}">Drivers</a> |
            <a href="{doc_url}"> Documentation</a>
            </p>
            """
        )
        label_versions.setOpenExternalLinks(True)
        label_versions.setWordWrap(True)

        layoutOverview.addWidget(label_versions)

        label_legal = QtWidgets.QLabel(
            f"""
            <p>
            Created by <b>Quentin Chateiller</b>, Python drivers originally from
            Quentin Chateiller and <b>Bruno Garbin</b>, for the C2N-CNRS
            (Center for Nanosciences and Nanotechnologies, Palaiseau, France)
            ToniQ team.
            <br>
            Project continued by <b>Jonathan Peltier</b>, for the C2N-CNRS
            Minaphot team and <b>Mathieu Jeannin</b>, for the C2N-CNRS
            Odin team.
            <br>
            <br>
            Distributed under the terms of the
            <a href="{project_url}/blob/master/LICENSE">GPL-3.0 licence</a>
            </p>"""
        )
        label_legal.setOpenExternalLinks(True)
        label_legal.setWordWrap(True)
        layoutLegal.addWidget(label_legal)

    def closeEvent(self, event):
        """ Does some steps before the window is really killed """
        # Delete reference of this window in the control center
        if hasattr(self.mainGui, 'clearAbout'): self.mainGui.clearAbout()

        if self.mainGui is None:
            QtWidgets.QApplication.quit()  # close the about app


def get_versions() -> dict:
    """Information about Autolab versions """

    # Based on Spyder about.py (https://github.com/spyder-ide/spyder/blob/3ce32d6307302a93957594569176bc84d9c1612e/spyder/plugins/application/widgets/about.py#L40)
    versions = {
        'autolab': __version__,
        'python': platform.python_version(),  # "2.7.3"
        'bitness': 64 if sys.maxsize > 2**32 else 32,
        'qt_api': qtpy.API_NAME,      # PyQt5
        'qt_api_ver': (qtpy.PYSIDE_VERSION if 'pyside' in qtpy.API
                       else qtpy.PYQT_VERSION),
        'system': platform.system(),   # Linux, Windows, ...
        'release': platform.release(),  # XP, 10.6, 2.2.0, etc.
        'pyqtgraph': pg.__version__,
        'numpy': np.__version__,
        'pandas': pd.__version__,
    }
    if sys.platform == 'darwin':
        versions.update(system='macOS', release=platform.mac_ver()[0])

    return versions
