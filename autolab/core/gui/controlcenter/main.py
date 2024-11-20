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
from typing import Any, Type, Union

import numpy as np
import pandas as pd
from qtpy import QtCore, QtWidgets, QtGui
import pyqtgraph as pg
from pyqtgraph.dockarea.DockArea import DockArea
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.console import ConsoleWidget

from .thread import ThreadManager
from .treewidgets import TreeWidgetItemModule
from ..scanning.main import Scanner
from ..GUI_instances import (openPlotter, closePlotter,
                             openAbout, closeAbout,
                             openAddDevice, closeAddDevice,
                             openVariablesMenu, closeVariablesMenu,
                             openPreferences, closePreferences,
                             openDriverInstaller, closeDriverInstaller,
                             closeMonitors,
                             closeSliders,
                             )
from ..icons import icons
from ...paths import PATHS
from ...devices import list_devices, list_loaded_devices, Device, close
from ...elements import Variable as Variable_og
from ...elements import Action
from ...config import get_control_center_config
from ...utilities import boolean, open_file
from ...web import report, doc


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


# Tree widget configuration
class MyQTreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, gui, parent=None):
        self.gui = gui
        super().__init__(parent)

    def startDrag(self, supportedActions):
        dragged_item = self.currentItem()

        if isinstance(dragged_item, TreeWidgetItemModule):
            return None

        if self.gui.scanner is not None:
            self.gui.scanner.setWindowState(
                self.gui.scanner.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.gui.scanner.activateWindow()
        super().startDrag(supportedActions)

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


class ControlCenter(QtWidgets.QMainWindow):
    """ Main Qt window, Used to control devices, open scanner... """

    def __init__(self):

        # Set up the user interface.
        super().__init__()

        # Window configuration
        self.setWindowTitle("AUTOLAB - Control Panel")
        self.setWindowIcon(icons['autolab'])
        self.setFocus()
        self.activateWindow()
        self.resize(570, 700)

        self.close_device_on_exit = True

        # Thread manager
        self.threadManager = ThreadManager(self)
        self.threadDeviceDict = {}
        self.threadItemDict = {}

        # Scanner
        self.scanner = None

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
        self._stop_timerQueue = False

        # Import Autolab config
        control_center_config = get_control_center_config()
        logger_active = boolean(control_center_config['logger'])
        console_active = boolean(control_center_config['console'])

        self._logger_area = None
        self._console_area = None
        self.stdout = None
        self.stderr = None

        self.init_ui()

        if logger_active:
            self.add_logger()

        if console_active:
            self.add_console()

    def init_ui(self):
        # Main frame configuration: centralWidget(verticalLayout(splitter(tree)))
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)

        verticalLayout = QtWidgets.QVBoxLayout(centralWidget)
        verticalLayout.setSpacing(0)
        verticalLayout.setContentsMargins(0,0,0,0)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        verticalLayout.addWidget(self.splitter)

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

        self.splitter.addWidget(self.tree)

        closeWidget = QtWidgets.QCheckBox('Disconnect devices on exit')
        closeWidget.setChecked(self.close_device_on_exit)
        closeWidget.stateChanged.connect(
            lambda state: setattr(self, 'close_device_on_exit', state))

        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.addStretch()
        horizontalLayout.addWidget(closeWidget)

        verticalLayout.addLayout(horizontalLayout)

        self.menuBar = self.menuBar()
        self.statusBar = self.statusBar()

        # Menu
        guiMenu = self.menuBar.addMenu('Panels')

        scanAction = guiMenu.addAction('Scanner')
        scanAction.setIcon(icons['scanner'])
        scanAction.triggered.connect(self.openScanner)
        scanAction.setStatusTip('Open the scanner in another window')

        plotAction = guiMenu.addAction('Plotter')
        plotAction.setIcon(icons['plotter'])
        plotAction.triggered.connect(lambda: openPlotter(has_parent=True))
        plotAction.setStatusTip('Open the plotter in another window')

        variablesMenuAction = guiMenu.addAction('Variables')
        variablesMenuAction.setIcon(icons['variables'])
        variablesMenuAction.triggered.connect(lambda: openVariablesMenu(True))
        variablesMenuAction.setStatusTip("Open the variable menu in another window")

        settingsMenu = self.menuBar.addMenu('Settings')

        Preferences = settingsMenu.addAction('Preferences')
        Preferences.setIcon(icons['preference'])
        Preferences.triggered.connect(lambda: openPreferences(gui=self))
        Preferences.setStatusTip("Open the preferences window")

        userFolder = settingsMenu.addAction('User folder')
        userFolder.setIcon(icons['folder'])
        userFolder.triggered.connect(self.openUserFolder)
        userFolder.setStatusTip("Open the user folder")

        settingsMenu.addSeparator()

        devicesConfig = settingsMenu.addAction('Devices config')
        devicesConfig.setIcon(icons['file'])
        devicesConfig.triggered.connect(self.openDevicesConfig)
        devicesConfig.setStatusTip("Open the devices configuration file")

        downloadDriverAction = settingsMenu.addAction('Download drivers')
        downloadDriverAction.setIcon(icons['read-save'])
        downloadDriverAction.triggered.connect(lambda: openDriverInstaller(gui=self))
        downloadDriverAction.setStatusTip("Open the utility to download drivers")

        settingsMenu.addSeparator()

        refreshAction = settingsMenu.addAction('Refresh devices')
        refreshAction.setIcon(icons['reload'])
        refreshAction.triggered.connect(self.initialize)
        refreshAction.setStatusTip('Reload devices setting')

        helpMenu = self.menuBar.addMenu('Help')

        reportAction = helpMenu.addAction('Report bugs / suggestions')
        reportAction.setIcon(icons['github'])
        reportAction.triggered.connect(report)
        reportAction.setStatusTip('Open the issue webpage of this project on GitHub')

        helpMenu.addSeparator()

        helpAction = helpMenu.addAction('Documentation (Online)')
        helpAction.setIcon(icons['readthedocs'])
        helpAction.triggered.connect(lambda: doc(True))
        helpAction.setStatusTip('Open the documentation on Read The Docs website')

        helpActionOffline = helpMenu.addAction('Documentation (Offline)')
        helpActionOffline.setIcon(icons['pdf'])
        helpActionOffline.triggered.connect(lambda: doc(False))
        helpActionOffline.setStatusTip(
            'Open the pdf documentation form local file ' \
            '(may no be up-to-day with online version)')

        helpMenu.addSeparator()

        aboutAction = helpMenu.addAction('About Autolab')
        aboutAction.setIcon(icons['autolab'])
        aboutAction.triggered.connect(lambda: openAbout(self))
        aboutAction.setStatusTip('Information about Autolab')
        # / Menu

    def update_handle(self):
        for splitter in (self.splitter, ):
            for i in range(splitter.count()):
                handle = splitter.handle(i)
                handle.setStyleSheet("background-color: #DDDDDD;")
                handle.installEventFilter(self)

    def activate_logger(self, activate: bool):
        if activate:
            self.add_logger()
        else:
            self.remove_logger()

    def add_logger(self):
        self.remove_logger()

        logger_area = DockArea(self)
        self._logger_area = logger_area
        self.splitter.addWidget(logger_area)

        logger_dock = Dock("Logger")
        logger_area.addDock(logger_dock, 'bottom')

        self.logger = QtWidgets.QTextBrowser(self)
        self.loggerDefaultColor = self.logger.textColor()

        # Set logger
        control_center_config = get_control_center_config()
        print_active = boolean(control_center_config['print'])
        self.stdout = OutputWrapper(self, True, True, print_active)
        self.stderr = OutputWrapper(self, False, True, print_active)
        self.stdout.outputWritten.connect(self.handleOutput)
        self.stderr.outputWritten.connect(self.handleOutput)

        logger_dock.addWidget(self.logger)

        self.update_handle()

    def remove_logger(self):
        if self._logger_area:
            self._logger_area.deleteLater()
            self._logger_area = None

            if self.stdout:
                sys.stdout = self.stdout._stream
                self.stdout = None

            if self.stderr:
                sys.stderr = self.stderr._stream
                self.stderr = None

    def activate_console(self, activate: bool):
        if activate:
            self.add_console()
        else:
            self.remove_console()

    def add_console(self):
        self.remove_console()

        import autolab
        namespace = {'np': np, 'pd': pd, 'autolab': autolab}
        text = """ Packages imported: autolab, numpy as np, pandas as pd.\n"""
        console_area = DockArea(self)
        self._console_area = console_area
        self.splitter.addWidget(console_area)

        console_dock = Dock("Console")
        console_area.addDock(console_dock, 'bottom')

        console_widget = ConsoleWidget(namespace=namespace, text=text)
        console_dock.addWidget(console_widget)

        self.update_handle()

    def remove_console(self):
        if self._console_area:
            self._console_area.deleteLater()
            self._console_area = None

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            obj.setStyleSheet("background-color: #AAAAAA;")  # Hover color
        elif event.type() == QtCore.QEvent.Leave:
            obj.setStyleSheet("background-color: #DDDDDD;")  # Normal color
        return super().eventFilter(obj, event)

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

        if self._stop_timerQueue:
            self.timerQueue.stop()
            self._stop_timerQueue = False

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
        addDeviceChoice = menu.addAction('Add Device')
        addDeviceChoice.setIcon(icons['add'])

        choice = menu.exec_(self.tree.viewport().mapToGlobal(position))

        if choice == addDeviceChoice:
            openAddDevice(gui=self)

    def itemClicked(self, item: QtWidgets.QTreeWidgetItem):
        """ Function called when a normal click has been detected in the tree.
            Check the association if it is a main item """
        if (item.parent() is None and not item.loaded
                and id(item) not in self.threadItemDict):
            self.threadItemDict[id(item)] = item  # needed before start of timer to avoid bad timing and to stop thread before loading is done
            item.setValueKnownState(0.5)  # yellow color
            self.threadManager.start(item, 'load')  # load device and add it to queue for timer to associate it later (doesn't block gui while device is openning)
            self.timerDevice.start()
            self.timerQueue.start()

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

    def clearScanner(self):
        """ This clear the scanner instance reference when quitted """
        self.scanner = None

    @staticmethod
    def openDevicesConfig():
        """ Open the devices configuration file """
        open_file(PATHS['devices_config'])

    @staticmethod
    def openUserFolder():
        """ Open the user folder """
        open_file(PATHS['user_folder'])

    def setScanParameter(self, recipe_name: str, param_name: str,
                         variable: Variable_og):
        """ Set the selected variable has parameter for the recipe """
        if self.scanner is None:
            self.openScanner()

        self.scanner.configManager.setParameter(recipe_name, param_name, variable)

    def addStepToScanRecipe(self, recipe_name: str, stepType: str,
                            element: Union[Variable_og, Action],
                            value: Any = None):
        """ Add the selected variable has a step for the recipe """
        if self.scanner is None:
            self.openScanner()

        self.scanner.configManager.addRecipeStep(
            recipe_name, stepType, element, value=value)

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

    def closeEvent(self, event):
        """ This function does some steps before the window is really killed """
        if self.scanner:
            self.scanner.close()

            if self.scanner is not None and self.scanner.isVisible():
                event.ignore()
                return None

        closePlotter()
        closeAbout()
        closeAddDevice()
        closeMonitors()
        closeSliders()
        closeVariablesMenu()
        closePreferences()
        closeDriverInstaller()

        if self.close_device_on_exit:
            close()  # close all devices

        self.remove_logger()
        self.remove_console()

        self.timerDevice.stop()
        self.timerQueue.stop()

        try:
            # Prevent 'RuntimeError: wrapped C/C++ object of type ViewBox has been deleted' when reloading gui
            for view in pg.ViewBox.AllViews.copy().keys():
                pg.ViewBox.forgetView(id(view), view)

            pg.ViewBox.quit()
        except: pass

        for children in self.findChildren(QtWidgets.QWidget):
            children.deleteLater()

        super().closeEvent(event)

        QtWidgets.QApplication.quit()  # close the app

        # OPTIMIZE: don't know if should erase variables on exit or not.
        # Currently decided to only erase variables defined by scanner itself,
        # keeping the ones defined by user.
        # VARIABLES.clear()  # reset variables defined in the GUI
