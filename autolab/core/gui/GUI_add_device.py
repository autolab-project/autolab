# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 14:39:02 2024

@author: Jonathan
"""
import sys

from qtpy import QtCore, QtWidgets

from .GUI_instances import clearAddDevice
from .icons import icons
from ..drivers import (list_drivers, load_driver_lib, get_connection_names,
                       get_driver_class, get_connection_class, get_class_args)
from ..config import get_all_devices_configs, save_config


class AddDeviceWindow(QtWidgets.QMainWindow):

    def __init__(self, parent: QtWidgets.QMainWindow = None):

        super().__init__(parent)
        self.mainGui = parent
        self.setWindowTitle('AUTOLAB - Add Device')
        self.setWindowIcon(icons['autolab'])

        self.statusBar = self.statusBar()

        self._prev_name = ''
        self._prev_conn = ''

        try:
            import pyvisa as visa
            self.rm = visa.ResourceManager()
        except:
            self.rm = None

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

        self.deviceNickname = QtWidgets.QLineEdit()
        self.deviceNickname.setText('my_device')

        layoutDeviceNickname.addWidget(label)
        layoutDeviceNickname.addWidget(self.deviceNickname)

        # Driver name
        layoutDriverName = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(layoutDriverName)

        label = QtWidgets.QLabel('Driver')

        self.driversComboBox = QtWidgets.QComboBox()
        self.driversComboBox.addItems(list_drivers())
        self.driversComboBox.activated.connect(self.driverChanged)
        self.driversComboBox.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToContents)

        layoutDriverName.addWidget(label)
        layoutDriverName.addStretch()
        layoutDriverName.addWidget(self.driversComboBox)

        # Driver connection
        layoutDriverConnection = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(layoutDriverConnection)

        label = QtWidgets.QLabel('Connection')

        self.connectionComboBox = QtWidgets.QComboBox()
        self.connectionComboBox.activated.connect(self.connectionChanged)
        self.connectionComboBox.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToContents)

        layoutDriverConnection.addWidget(label)
        layoutDriverConnection.addStretch()
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
        addOptionalArg.setIcon(icons['add'])
        addOptionalArg.clicked.connect(lambda state: self.addOptionalArgClicked())

        layoutButtonArg.addWidget(addOptionalArg)
        layoutButtonArg.setAlignment(QtCore.Qt.AlignLeft)

        # Add device
        layoutButton = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(layoutButton)

        self.addButton = QtWidgets.QPushButton('Add Device')
        self.addButton.clicked.connect(self.addButtonClicked)

        layoutButton.addWidget(self.addButton)

        # update driver name combobox
        self.driverChanged()

        self.resize(self.minimumSizeHint())

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
        widget.setIcon(icons['remove'])
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

        self.setWindowTitle('AUTOLAB - Modify device')
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
        if index != -1:
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
        if driver_name == '':
            self.setStatus(f"Can't load driver associated with {self.deviceNickname.text()}", 10000, False)
            return None
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
        try:
            driver_lib = load_driver_lib(driver_name)
        except:
            return None

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
        clearAddDevice()

        if not self.mainGui:
            QtWidgets.QApplication.quit()  # close the monitor app
