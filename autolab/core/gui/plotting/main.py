# -*- coding: utf-8 -*-
"""
Created on Oct 2022

@author: jonathan based on qchat
"""
import os
import sys
import queue
import time
import uuid
from typing import Any, Type

from qtpy import QtCore, QtWidgets, uic, QtGui

from .figure import FigureManager
from .data import DataManager
from .thread import ThreadManager
from .treewidgets import TreeWidgetItemModule
from ..icons import icons
from ... import devices
from ... import config
from ..GUI_utilities import get_font_size, setLineEditBackground


class MyQTreeWidget(QtWidgets.QTreeWidget):

    reorderSignal = QtCore.Signal(object)

    def __init__(self,parent, plotter):
        self.plotter = plotter
        QtWidgets.QTreeWidget.__init__(self,parent)

        self.setAcceptDrops(True)

    def dropEvent(self, event):
        """ This function is used to add a plugin to the plotter """
        variable = event.source().last_drag
        if isinstance(variable, str):
            self.plotter.addPlugin(variable)
        self.setGraphicsEffect(None)

    def dragEnterEvent(self, event):

        if (event.source() is self) or (
                hasattr(event.source(), "last_drag") and isinstance(event.source().last_drag, str)):
            event.accept()
            shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=3, yOffset=3)
            self.setGraphicsEffect(shadow)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setGraphicsEffect(None)


class Plotter(QtWidgets.QMainWindow):

    def __init__(self,mainGui):

        self.active = False
        self.mainGui = mainGui
        self.all_plugin_list = []
        self.active_plugin_dict = {}

        self._font_size = get_font_size() + 1

        # Configuration of the window
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__),'interface.ui')
        uic.loadUi(ui_path,self)
        self.setWindowTitle("AUTOLAB - Plotter")
        self.setWindowIcon(QtGui.QIcon(icons['plotter']))

        # Loading of the different centers
        self.figureManager = FigureManager(self)
        self.dataManager = DataManager(self)

        self.threadManager = ThreadManager(self)
        self.threadDeviceDict = {}
        self.threadItemDict = {}

        # Save button
        self.save_pushButton.clicked.connect(self.dataManager.saveButtonClicked)
        self.save_pushButton.setEnabled(False)

        # Clear button
        self.clear_pushButton.clicked.connect(self.dataManager.clear)
        self.clear_all_pushButton.clicked.connect(self.dataManager.clear_all)
        self.clear_pushButton.setEnabled(False)
        self.clear_all_pushButton.setEnabled(False)

        # Open button
        self.openButton.clicked.connect(self.dataManager.importActionClicked)

        # comboBox with data id
        self.data_comboBox.activated.connect(self.dataManager.data_comboBoxClicked)

        # Number of traces
        self.nbTraces_lineEdit.setText(f'{self.figureManager.nbtraces:g}')
        self.nbTraces_lineEdit.returnPressed.connect(self.nbTracesChanged)
        self.nbTraces_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.nbTraces_lineEdit,'edited', self._font_size))
        setLineEditBackground(self.nbTraces_lineEdit, 'synced', self._font_size)

        getattr(self, 'variable_x_comboBox').currentIndexChanged.connect(
            self.variableChanged)
        getattr(self, 'variable_y_comboBox').currentIndexChanged.connect(
            self.variableChanged)

        self.device_lineEdit.setText(f'{self.dataManager.deviceValue}')
        self.device_lineEdit.returnPressed.connect(self.deviceChanged)
        self.device_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.device_lineEdit, 'edited', self._font_size))
        setLineEditBackground(self.device_lineEdit, 'synced', self._font_size)

        # Plot button
        self.plotDataButton.clicked.connect(self.refreshPlotData)

        # Timer
        self.timer_time = 0.5  # This plotter is not meant for fast plotting like the monitor, be aware it may crash with too high refreshing rate
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(int(self.timer_time*1000)) # ms
        self.timer.timeout.connect(self.autoRefreshPlotData)

        self.auto_plotDataButton.clicked.connect(self.autoRefreshChanged)
        self.overwriteDataButton.clicked.connect(self.overwriteDataChanged)

        # Delay
        self.delay_lineEdit.setText(str(self.timer_time))
        self.delay_lineEdit.returnPressed.connect(self.delayChanged)
        self.delay_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.delay_lineEdit, 'edited', self._font_size))
        setLineEditBackground(self.delay_lineEdit, 'synced', self._font_size)

        self.setAcceptDrops(True)

        # timer to load plugin to tree
        self.timerPlugin = QtCore.QTimer(self)
        self.timerPlugin.setInterval(50) # ms
        self.timerPlugin.timeout.connect(self.timerAction)

        # queue and timer to add/remove plot from plugin
        self.queue_driver = queue.Queue()
        self.dict_widget = {}
        self.timerQueue = QtCore.QTimer(self)
        self.timerQueue.setInterval(int(50)) # ms
        self.timerQueue.timeout.connect(self._queueDriverHandler)
        self.timerQueue.start()  # OPTIMIZE: should be started only when needed but difficult to know it before openning device which occurs in a diff thread! (can't start timer on diff thread)

        self.processPlugin()

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
                try: self.figureManager.fig.addItem(widget)
                except: pass
            elif action == "remove":
                d = self.dict_widget
                if widget is not None:
                    widget_pos = list(d.values()).index(widget)
                    if widget_pos is not None:
                        widget_name = list(d.keys())[widget_pos]
                        widget = d.get(widget_name)
                        if widget is not None:
                            widget = d.pop(widget_name)
                            try: self.figureManager.fig.removeItem(widget)
                            except: pass

    def timerAction(self):
        """ This function checks if a module has been loaded and put to the queue. If so, associate item and module """
        threadItemDictTemp = self.threadItemDict.copy()
        threadDeviceDictTemp = self.threadDeviceDict.copy()

        for item_id in threadDeviceDictTemp.keys():

            item = threadItemDictTemp[item_id]
            module = threadDeviceDictTemp[item_id]

            self.associate(item, module)
            item.setExpanded(True)

            self.threadItemDict.pop(item_id)
            self.threadDeviceDict.pop(item_id)

        if len(threadItemDictTemp) == 0:
            self.timerPlugin.stop()

    def itemClicked(self, item):
        """ Function called when a normal click has been detected in the tree.
            Check the association if it is a main item """
        if item.parent() is None and item.loaded is False and id(item) not in self.threadItemDict.keys():
            self.threadItemDict[id(item)] = item  # needed before start of timer to avoid bad timing and to stop thread before loading is done
            self.threadManager.start(item, 'load')  # load device and add it to queue for timer to associate it later (doesn't block gui while device is openning)
            self.timerPlugin.start()

    def rightClick(self, position):
        """ Function called when a right click has been detected in the tree """
        item = self.tree.itemAt(position)
        if hasattr(item,'menu'):
            item.menu(position)

    def processPlugin(self):

        # Create frame
        self.frame = QtWidgets.QFrame()
        self.splitter_2.insertWidget(1, self.frame)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layout = QtWidgets.QVBoxLayout(self.frame)

        label = QtWidgets.QLabel('Plugin:', self.frame)
        label.setToolTip("Drag and drop a device from the control panel to add a plugin to the plugin tree")
        layout.addWidget(label)
        font = QtGui.QFont()
        font.setBold(True)
        label.setFont(font)

        # Tree widget configuration
        self.tree = MyQTreeWidget(self.frame, self)
        layout.addWidget(self.tree)
        self.tree.setHeaderLabels(['Plugin','Type','Actions','Values',''])
        self.tree.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.tree.header().resizeSection(0, 170)
        self.tree.header().hideSection(1)
        self.tree.header().resizeSection(2, 50)
        self.tree.header().resizeSection(3, 70)
        self.tree.header().resizeSection(4, 15)
        self.tree.header().setStretchLastSection(False)
        self.tree.setAlternatingRowColors(True)

        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.itemClicked.connect(self.itemClicked)
        self.tree.customContextMenuRequested.connect(self.rightClick)

        plotter_config = config.load_config("plotter")

        if 'plugin' in plotter_config.sections() and len(plotter_config['plugin']) != 0:
            self.splitter_2.setSizes([200,300,80,80])
            for plugin_nickname in plotter_config['plugin'].keys() :
                plugin_name = plotter_config['plugin'][plugin_nickname]
                self.addPlugin(plugin_name, plugin_nickname)
        else:
            self.splitter.setSizes([400,40])
            self.splitter_2.setSizes([200,80,80,80])

    def addPlugin(self, plugin_name, plugin_nickname=None):

        if plugin_nickname is None:
            plugin_nickname = plugin_name

        if plugin_name in devices.list_devices():
            plugin_nickname = self.getUniqueName(plugin_nickname)
            self.all_plugin_list.append(plugin_nickname)
            item = TreeWidgetItemModule(self.tree,plugin_name,plugin_nickname,self)
            item.setBackground(0, QtGui.QColor('#9EB7F5'))  # blue

            self.itemClicked(item)
        else:
            self.setStatus(f"Error: plugin {plugin_name} not found in devices_config.ini",10000, False)

    def associate(self, item, module):

        item.load(module)
        self.active_plugin_dict[item.nickname] = module

        read_init_list = module._read_init_list
        for mod in module._mod.values():
            read_init_list.extend(mod._read_init_list)
        for variable in read_init_list:
            try:
                variable()
            except:
                self.setStatus(f"Can't read variable {variable.address()} on instantiation", 10000, False)
        try:
            data = self.dataManager.getLastSelectedDataset().data
            data = data[[self.figureManager.getLabel("x"),self.figureManager.getLabel("y")]].copy()
            module.instance.refresh(data)
        except Exception:
            pass

    def getUniqueName(self, basename: str):
        """ This function adds a number next to basename in case this basename is already taken """
        names = self.all_plugin_list
        name = basename

        compt = 0
        while True:
            if name in names:
                compt += 1
                name = basename+'_'+str(compt)
            else:
                break
        return name

    def dropEvent(self, event):
        """ Import data from filenames dropped """
        filenames = [e.toLocalFile() for e in event.mimeData().urls()]
        self.dataManager.importAction(filenames)

        qwidget_children = self.findChildren(QtWidgets.QWidget)
        for widget in qwidget_children:
            widget.setGraphicsEffect(None)

    def dragEnterEvent(self, event):
        """ Check that drop filenames """
        # only accept if there is at least one filename in the dropped filenames -> refuse folders
        if event.mimeData().hasUrls() and any([os.path.isfile(e.toLocalFile()) for e in event.mimeData().urls()]):
            event.accept()

            qwidget_children = self.findChildren(QtWidgets.QWidget)
            for widget in qwidget_children:
                shadow = QtWidgets.QGraphicsColorizeEffect()
                shadow.setColor(QtGui.QColor(20,20,20))
                shadow.setStrength(1)
                widget.setGraphicsEffect(shadow)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        qwidget_children = self.findChildren(QtWidgets.QWidget)
        for widget in qwidget_children:
            widget.setGraphicsEffect(None)

    def plugin_refresh(self):
        if self.active_plugin_dict:
            self.clearStatus()
            if hasattr(self.dataManager.getLastSelectedDataset(),"data"):
                data = self.dataManager.getLastSelectedDataset().data
                data = data[[self.figureManager.getLabel("x"),self.figureManager.getLabel("y")]].copy()
            else:
                data = None

            for module in self.active_plugin_dict.values():
                if hasattr(module.instance, "refresh"):
                    try:
                        module.instance.refresh(data)
                    except Exception as error:
                        self.setStatus(f"Error in plugin {module.name}: '{error}'",10000, False)

    def overwriteDataChanged(self):
        """ Set overwrite name for data import """
        self.dataManager.setOverwriteData(self.overwriteDataButton.isChecked())

    def autoRefreshChanged(self):
        """ Set if auto refresh call for device data """
        if self.auto_plotDataButton.isChecked():
            self.timer.start()
        else:
            self.timer.stop()

    def autoRefreshPlotData(self):
        """ Function that refresh plot every timer interval """
        # OPTIMIZE: timer should not call a heavy function, idealy just take data to plot
        self.refreshPlotData()

    def refreshPlotData(self):
        """ This function get the last dataset data and display it onto the Plotter GUI """
        deviceValue = self.dataManager.getDeviceValue()

        try:
            deviceVariable = self.dataManager.getDeviceName(deviceValue)
            dataset = self.dataManager.importDeviceData(deviceVariable)
            data_name = dataset.name
            self.figureManager.start(dataset)
            self.setStatus(f"Display the data: '{data_name}'", 5000)
        except Exception as error:
            self.setStatus(f"Can't refresh data: {error}", 10000, False)

    def deviceChanged(self):
        """ This function start the update of the target value in the data manager
        when a changed has been detected """
        # Send the new value
        try:
            value = str(self.device_lineEdit.text())
            self.dataManager.setDeviceValue(value)
        except Exception as er:
            self.setStatus(f"ERROR Can't change device variable: {er}", 10000, False)
        else:
            # Rewrite the GUI with the current value
            self.updateDeviceValueGui()

    def updateDeviceValueGui(self):
        """ This function ask the current value of the target value in the data
        manager, and then update the GUI """
        value = self.dataManager.getDeviceValue()
        self.device_lineEdit.setText(f'{value}')
        setLineEditBackground(self.device_lineEdit, 'synced', self._font_size)

    def variableChanged(self,index):
        """ This function is called when the displayed result has been changed in
        the combo box. It proceeds to the change. """
        self.figureManager.clearData()

        if self.variable_x_comboBox.currentIndex() != -1 and self.variable_y_comboBox.currentIndex() != -1 :
            self.figureManager.reloadData()

    def nbTracesChanged(self):
        """ This function is called when the number of traces displayed has been changed
        in the GUI. It proceeds to the change and update the plot. """
        value = self.nbTraces_lineEdit.text()

        check = False
        try:
            value = int(float(value))
            assert value > 0
            self.figureManager.nbtraces = value
            check = True
        except:
            pass

        self.nbTraces_lineEdit.setText(f'{self.figureManager.nbtraces:g}')
        setLineEditBackground(self.nbTraces_lineEdit, 'synced', self._font_size)

        if check is True and self.variable_y_comboBox.currentIndex() != -1:
            self.figureManager.reloadData()

    def closeEvent(self,event):
        """ This function does some steps before the window is closed (not killed) """
        self.timer.stop()
        self.timerPlugin.stop()
        self.timerQueue.stop()

        self.mainGui.clearPlotter()

    def close(self):
        """ This function does some steps before the window is killed """
        for children in self.findChildren(
                QtWidgets.QWidget, options=QtCore.Qt.FindDirectChildrenOnly):
            children.deleteLater()

        super().close()

    def delayChanged(self):
        """ This function start the update of the delay in the thread manager
        when a changed has been detected """
        # Send the new value
        try:
            value = float(self.delay_lineEdit.text())
            assert value >= 0
            self.timer_time = value
        except:
            pass

        # Rewrite the GUI with the current value
        self.updateDelayGui()

    def updateDelayGui(self):
        """ This function ask the current value of the delay in the data
        manager, and then update the GUI """

        value = self.timer_time
        self.delay_lineEdit.setText(f'{value:g}')
        self.timer.setInterval(int(value*1000))  # ms
        setLineEditBackground(self.delay_lineEdit, 'synced', self._font_size)

    def setStatus(self,message, timeout=0, stdout=True):
        """ Modify the message displayed in the status bar and add error message to logger """
        self.statusBar.showMessage(message, timeout)
        if not stdout: print(message, file=sys.stderr)

    def clearStatus(self):
        """ Erase the message displayed in the status bar """
        self.setStatus('')
