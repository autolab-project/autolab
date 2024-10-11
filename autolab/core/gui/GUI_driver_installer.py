# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 10:46:14 2024

@author: jonathan
"""
import sys

from qtpy import QtWidgets, QtGui

from .icons import icons
from .GUI_instances import clearDriverInstaller
from ..paths import DRIVER_SOURCES, DRIVER_REPOSITORY
from ..repository import install_drivers, _download_driver, _get_drivers_list_from_github
from ..drivers import update_drivers_paths


class DriverInstaller(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        """ GUI to select which driver to install from the official github repo """

        super().__init__()

        self.setWindowTitle("AUTOLAB - Driver Installer")
        self.setWindowIcon(icons['autolab'])
        self.setFocus()
        self.activateWindow()

        self.statusBar = self.statusBar()

        official_folder = DRIVER_SOURCES['official']
        official_url = DRIVER_REPOSITORY[official_folder]

        list_driver = []
        try:
            list_driver = _get_drivers_list_from_github(official_url)
        except:
            self.setStatus(f'Warning: Cannot access {official_url}', 10000, False)

        self.mainGui = parent
        self.url = official_url  # TODO: use dict DRIVER_REPOSITORY to have all urls
        self.list_driver = list_driver
        self.OUTPUT_DIR = official_folder

        self.init_ui()

        self.adjustSize()

    def init_ui(self):
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)

        # OFFICIAL DRIVERS
        formLayout = QtWidgets.QFormLayout()
        centralWidget.setLayout(formLayout)

        self.masterCheckBox = QtWidgets.QCheckBox(f"From {DRIVER_REPOSITORY[DRIVER_SOURCES['official']]}:")
        self.masterCheckBox.setChecked(False)
        self.masterCheckBox.stateChanged.connect(self.masterCheckBoxChanged)
        formLayout.addRow(self.masterCheckBox)

        # Init table size
        sti = QtGui.QStandardItemModel()
        for i in range(len(self.list_driver)):
            sti.appendRow([QtGui.QStandardItem(str())])

        # Create table
        tab = QtWidgets.QTableView()
        tab.setModel(sti)
        tab.verticalHeader().setVisible(False)
        tab.horizontalHeader().setVisible(False)
        tab.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        tab.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        tab.setAlternatingRowColors(True)
        tab.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                          QtWidgets.QSizePolicy.Expanding)
        tab.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)

        if self.list_driver:  # OPTIMIZE: c++ crash if no driver in list!
            tab.horizontalHeader().setSectionResizeMode(
                0, QtWidgets.QHeaderView.ResizeToContents)

        # Init checkBox
        self.list_checkBox = []
        for i, driver_name in enumerate(self.list_driver):
            checkBox = QtWidgets.QCheckBox(f"{driver_name}")
            checkBox.setChecked(False)
            self.list_checkBox.append(checkBox)
            tab.setIndexWidget(sti.index(i, 0), checkBox)

        formLayout.addRow(QtWidgets.QLabel(""), tab)

        download_pushButton = QtWidgets.QPushButton()
        download_pushButton.clicked.connect(self.installListDriver)
        download_pushButton.setText("Download")
        formLayout.addRow(download_pushButton)

    def masterCheckBoxChanged(self):
        """ Checked all the checkBox related to the official github repo """
        state = self.masterCheckBox.isChecked()
        for checkBox in self.list_checkBox:
            checkBox.setChecked(state)

    def installListDriver(self):
        """ Install all the drivers for which the corresponding checkBox has been checked """
        list_bool = [
            checkBox.isChecked() for checkBox in self.list_checkBox]
        list_driver_to_download = [
            driver_name for (driver_name, driver_bool) in zip(
                self.list_driver, list_bool) if driver_bool]

        try:
            # Better for all drivers
            if all(list_bool):
                install_drivers(skip_input=True)
            # Better for several drivers
            elif any(list_bool):
                for driver_name in list_driver_to_download:
                    # self.setStatus(f"Downloading {driver_name}", 5000)  # OPTIMIZE: currently thread blocked by installer so don't show anything until the end
                    e = _download_driver(
                        self.url, driver_name, self.OUTPUT_DIR, _print=False)
                    if e is not None:
                        print(e, file=sys.stderr)
                        # self.setStatus(e, 10000, False)
        except Exception as e:
            self.setStatus(f'Error: {e}', 10000, False)
        else:
            self.setStatus('Finished!', 5000)

        # Update available drivers
        update_drivers_paths()

    def closeEvent(self, event):
        """ This function does some steps before the window is really killed """
        clearDriverInstaller()

        super().closeEvent(event)

        if not self.mainGui:
            QtWidgets.QApplication.quit()  # close the app

    def setStatus(self, message: str, timeout: int = 0, stdout: bool = True):
        """ Modify the message displayed in the status bar and add error message to logger """
        self.statusBar.showMessage(message, timeout)
        if not stdout: print(message, file=sys.stderr)
