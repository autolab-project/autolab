# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 18:16:20 2023

@author: Jonathan
"""

import os
import sys
import urllib.request

from . import paths
from .gitdir import download


DRIVER_LIST_NAME = 'driver_list.txt'
OUTPUT_DIR = paths.DRIVER_SOURCES["official"]


def _format_url(url):
    """ Return the correct path to the text file in a github repo """

    if not url.endswith(DRIVER_LIST_NAME):
        if not ('/blob/' in url or '/tree/' in url):
            url += '/tree/master'
        url += "/" + DRIVER_LIST_NAME

    if url.startswith('https://github.com'):
        url = 'https://raw.githubusercontent.com'+url.split('https://github.com')[1].replace('/blob/', '/').replace('/tree/', '/')

    return url

GITHUB_OFFICIAL = _format_url(paths.DRIVER_GITHUB['official'])


def _get_drivers_list_from_github(url):
    """ Returns a list of the available drivers on a github repo.
    url is the url of a file containing a list of the available drivers \
    It can also be the url of the folder containing the file and drivers.
    Available drivers must be in the same folder as the file.
    """
    url = _format_url(url)

    with urllib.request.urlopen(url) as f:
        html = f.read().decode('utf-8')

    driver_list = html.split("\n")

    return driver_list


def _download_drivers(url, driver_list, output_dir):
    """ Download drivers from an github url """
    if len(driver_list) != 0:
        print(f"Drivers will be downloaded to {output_dir}")
    for driver_name in driver_list:
        _download_driver(url, driver_name, output_dir)
    print('Done!')


def _download_driver(url, driver_name, output_dir):
    """ Download a driver from an github url """
    try :
        print(f"Downloading {driver_name}")
        driver_url = url + "/" + driver_name
        # BUG: too slow to be used, need to find better solution
        # BUG: got 'HTTP Error 403: rate limit exceeded' due to too much download
        # -> must find another solution to download repo (without git if possible)
        #
        download(driver_url, output_dir=output_dir, _print=True)
    except:  # OPTIMIZE: if use Exception, crash python when having error
        print(f"Error with {driver_name}", file=sys.stderr)


def _check_empty_driver_folder():
    if not os.listdir(paths.DRIVER_SOURCES['official']):
        print(f"No drivers found in {paths.DRIVER_SOURCES['main']}")
        ans = input('Do you want to install drivers? [default:yes] > ')
        if ans.strip().lower() == 'no':
            pass
        else:
            install_drivers()


def driver_list():
    """ Returns the list of all the drivers from the official github repo """
    return _get_drivers_list_from_github(paths.DRIVER_GITHUB['official'])


def install_drivers():
    """ Ask the user which driver to install from the official autolab driver github repo.
    If PyQt5 is install, open a GUI to select the driver.
    Else, prompt the user to install all the drivers or individual drivers. """

    try:
        from PyQt5 import QtWidgets, QtGui
    except:
        print("No PyQt5 installed. Using the console to install drivers instead")
        list_driver = driver_list()

        ans = input('Do you want to install all the official drivers? [default:yes] > ')
        if ans.strip().lower() == 'no':
            print(f"Drivers will be downloaded to {OUTPUT_DIR}")
            for i, driver_name in enumerate(list_driver):
                ans = input(f'Download {driver_name}? [default:yes] > ')
                if ans.strip().lower() != 'no':
                    _download_driver(paths.DRIVER_GITHUB['official'], driver_name, OUTPUT_DIR)
        else:
            _download_drivers(paths.DRIVER_GITHUB['official'], list_driver, OUTPUT_DIR)
    else:

        class DriverInstaller(QtWidgets.QMainWindow):

            def __init__(self):
                """ GUI to select which driver to install from the official github repo """

                QtWidgets.QMainWindow.__init__(self)

                self.setWindowTitle("Autolab Driver Installer")
                self.setFocus()
                self.activateWindow()

                centralWidget = QtWidgets.QWidget()
                self.setCentralWidget(centralWidget)

                # OPTIMIZE: for url_txt in paths.DRIVER_GITHUB

                # OFFICIAL DRIVERS
                formLayout = QtWidgets.QFormLayout()

                self.masterCheckBox = QtWidgets.QCheckBox(f"From {paths.DRIVER_GITHUB['official']}:")
                self.masterCheckBox.setChecked(True)
                self.masterCheckBox.stateChanged.connect(self.masterCheckBoxChanged)
                formLayout.addRow(self.masterCheckBox)

                self.list_driver = driver_list()

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
                tab.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
                tab.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                tab.setSizeAdjustPolicy(tab.AdjustToContents)

                # Init checkBox
                self.list_checkBox = []
                for i, driver_name in enumerate(self.list_driver):
                    checkBox = QtWidgets.QCheckBox(f"{driver_name}")
                    checkBox.setChecked(True)
                    self.list_checkBox.append(checkBox)
                    tab.setIndexWidget(sti.index(i, 0), checkBox)

                formLayout.addRow(QtWidgets.QLabel(""), tab)

                download_pushButton = QtWidgets.QPushButton()
                download_pushButton.clicked.connect(self.installListDriver)
                download_pushButton.setText("Download")
                formLayout.addRow(download_pushButton)

                centralWidget.setLayout(formLayout)

            def masterCheckBoxChanged(self):

                """ Checked all the checkBox related to the official github repo """

                state = self.masterCheckBox.isChecked()
                for checkBox in self.list_checkBox:
                    checkBox.setChecked(state)

            def closeEvent(self,event):

                """ This function does some steps before the window is really killed """

                QtWidgets.QApplication.quit()  # close the interface

            def installListDriver(self):

                """ Install all the drivers for which the corresponding checkBox has been checked """

                list_bool = [checkBox.isChecked() for checkBox in self.list_checkBox]

                list_driver_to_download = [driver_name for (driver_name, driver_bool) in zip(self.list_driver, list_bool) if driver_bool]
                _download_drivers(paths.DRIVER_GITHUB['official'], list_driver_to_download, OUTPUT_DIR)


        print("Open driver installer")
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])

        driverInstaller = DriverInstaller()
        driverInstaller.show()
        app.exec_()
