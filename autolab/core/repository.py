# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 18:16:20 2023

@author: Jonathan
"""

import os
# import sys
import urllib.request
import zipfile
import tempfile
import shutil

from . import paths
# from .gitdir import download


# DRIVER_LIST_NAME = 'driver_list.txt'
# OUTPUT_DIR = paths.DRIVER_SOURCES["official"]


# def _format_url(url):
#     """ Return the correct path to the text file in a github repo """

#     if not url.endswith(DRIVER_LIST_NAME):
#         if not ('/blob/' in url or '/tree/' in url):
#             url += '/tree/master'
#         url += "/" + DRIVER_LIST_NAME

#     if url.startswith('https://github.com'):
#         url = 'https://raw.githubusercontent.com'+url.split('https://github.com')[1].replace('/blob/', '/').replace('/tree/', '/')

#     return url


def _format_url(url):
    """ Change github repo name to download link """

    if url.endswith(".zip"):
        format_url = url
    else:
        format_url = url if "/tree/" in url else url + "/tree/master"
        format_url = format_url.replace("/tree/", "/archive/refs/heads/")
        format_url += ".zip"
    return format_url


# GITHUB_OFFICIAL = _format_url(paths.DRIVER_GITHUB['official'])


# def _get_drivers_list_from_github(url):
#     """ Returns a list of the available drivers on a github repo.
#     url is the url of a file containing a list of the available drivers \
#     It can also be the url of the folder containing the file and drivers.
#     Available drivers must be in the same folder as the file.
#     """
#     url = _format_url(url)

#     with urllib.request.urlopen(url) as f:
#         html = f.read().decode('utf-8')

#     driver_list = html.split("\n")

#     return driver_list


def _download_repo(url, output_dir):
    with urllib.request.urlopen(url) as github_repo_zip:
        with open(output_dir, 'wb') as repo_zip:
            repo_zip.write(github_repo_zip.read())


def _unzip_repo(repo_zip, output_dir):
    """ Unzip repo_zip to output_dir using a temporary folder"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    temp_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(repo_zip, 'r') as zip_open:
        repo_name = zip_open.namelist()[0]
        zip_open.extractall(temp_dir)

    temp_unzip_repo = os.path.join(temp_dir, repo_name)

    for filename in os.listdir(temp_unzip_repo):
        temp_file = os.path.join(temp_unzip_repo, filename)
        output_file = os.path.join(output_dir, filename)

        if os.path.isfile(temp_file):
            shutil.copy(temp_file, output_file)
            os.remove(temp_file)
        else:
            try:
                shutil.copytree(temp_file, output_file, dirs_exist_ok=True)  # python >=3.8 only
            except:
                if os.path.exists(output_file):
                    shutil.rmtree(output_file, ignore_errors=True)
                shutil.copytree(temp_file, output_file)

            shutil.rmtree(temp_file, ignore_errors=True)

    os.rmdir(temp_unzip_repo)
    os.rmdir(temp_dir)


# def _download_drivers(url, driver_list, output_dir):
#     """ Download drivers from an github url """
#     if len(driver_list) != 0:
#         print(f"Drivers will be downloaded to {output_dir}")
#     for driver_name in driver_list:
#         _download_driver(url, driver_name, output_dir)
#     print('Done!')


# def _download_driver(url, driver_name, output_dir):
#     """ Download a driver from an github url """
#     try :
#         print(f"Downloading {driver_name}")
#         driver_url = url + "/" + driver_name
#         # BUG: too slow to be used, need to find better solution
#         # BUG: got 'HTTP Error 403: rate limit exceeded' due to too much download -> 60 requests/h should be enought if 1 package = 1 request but 1 package = nb_files requests
#         # -> must find another solution to download repo (without git if possible)
#         # https://stackoverflow.com/questions/7106012/download-a-single-folder-or-directory-from-a-github-repo
#         # https://stackoverflow.com/questions/33066582/how-to-download-a-folder-from-github
#         # https://www.gitkraken.com/learn/git/github-download
#         # https://github.com/Nordgaren/Github-Folder-Downloader/blob/master/gitdl.py
#         download(driver_url, output_dir=output_dir, _print=True)
#     except:  # OPTIMIZE: if use Exception, crash python when having error
#         print(f"Error with {driver_name}", file=sys.stderr)


def input_wrap(*args):

    """ Wrap input function to avoid crash with Spyder using Qtconsole=5.3 """

    input_allowed = True
    try:
        import spyder_kernels
        import qtconsole
    except ModuleNotFoundError:
        pass
    else:
        if hasattr(spyder_kernels, "console") and hasattr(qtconsole, "__version__"):
            if qtconsole.__version__.startswith("5.3"):
                print("Warning: Spyder crashes with input() if Qtconsole=5.3, skip user input.")
                input_allowed = False
    if input_allowed:
        ans = input(*args)
    else:
        ans = "yes"

    return ans


def _check_empty_driver_folder():
    if not os.listdir(paths.DRIVER_SOURCES['official']):
        print(f"No drivers found in {paths.DRIVER_SOURCES['official']}")
        install_drivers()


# def driver_list():
#     """ Returns the list of all the drivers from the official github repo """
#     return _get_drivers_list_from_github(paths.DRIVER_GITHUB['official'])


def install_drivers():
    """ Ask if want to install all the official drivers. """
    # """ Ask the user which driver to install from the official autolab driver github repo.
    # If PyQt5 is install, open a GUI to select the driver.
    # Else, prompt the user to install all the drivers or individual drivers. """

    # try:
    #     from PyQt5 import QtWidgets, QtGui
    # except:
        # print("No PyQt5 installed. Using the console to install drivers instead")
        # list_driver = driver_list()
    temp_repo_folder = tempfile.mkdtemp()

    for github_repo_url in paths.DRIVER_GITHUB.values():
        github_repo_zip_url = _format_url(github_repo_url)
        zip_name = "-".join((os.path.basename(github_repo_url),
                             os.path.basename(github_repo_zip_url)))
        temp_repo_zip = os.path.join(temp_repo_folder, zip_name)

        ans = input_wrap(f'Do you want to install all the drivers from {github_repo_url}? [default:yes] > ')
        if ans.strip().lower() == 'no':
            continue
        else:
            print(f"Downloading {github_repo_zip_url}")
            _download_repo(github_repo_zip_url, temp_repo_zip)
            print(f'Moving drivers to {paths.DRIVER_SOURCES["official"]}')
            _unzip_repo(temp_repo_zip, paths.DRIVER_SOURCES["official"])
            os.remove(temp_repo_zip)
    os.rmdir(temp_repo_folder)

        # print(f"Drivers will be downloaded to {OUTPUT_DIR}")
        # for i, driver_name in enumerate(list_driver):
        #     ans = input(f'Download {driver_name}? [default:yes] > ')
        #     if ans.strip().lower() != 'no':
        #         _download_driver(paths.DRIVER_GITHUB['official'], driver_name, OUTPUT_DIR)
    # else:

    # else:

    #     class DriverInstaller(QtWidgets.QMainWindow):

    #         def __init__(self):
    #             """ GUI to select which driver to install from the official github repo """

    #             QtWidgets.QMainWindow.__init__(self)

    #             self.setWindowTitle("Autolab Driver Installer")
    #             self.setFocus()
    #             self.activateWindow()

    #             centralWidget = QtWidgets.QWidget()
    #             self.setCentralWidget(centralWidget)

    #             # OPTIMIZE: for url_txt in paths.DRIVER_GITHUB

    #             # OFFICIAL DRIVERS
    #             formLayout = QtWidgets.QFormLayout()

    #             self.masterCheckBox = QtWidgets.QCheckBox(f"From {paths.DRIVER_GITHUB['official']}:")
    #             self.masterCheckBox.setChecked(True)
    #             self.masterCheckBox.stateChanged.connect(self.masterCheckBoxChanged)
    #             formLayout.addRow(self.masterCheckBox)

    #             self.list_driver = driver_list()

    #             # Init table size
    #             sti = QtGui.QStandardItemModel()
    #             for i in range(len(self.list_driver)):
    #                 sti.appendRow([QtGui.QStandardItem(str())])

    #             # Create table
    #             tab = QtWidgets.QTableView()
    #             tab.setModel(sti)
    #             tab.verticalHeader().setVisible(False)
    #             tab.horizontalHeader().setVisible(False)
    #             tab.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    #             tab.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
    #             tab.setAlternatingRowColors(True)
    #             tab.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    #             tab.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    #             tab.setSizeAdjustPolicy(tab.AdjustToContents)

    #             # Init checkBox
    #             self.list_checkBox = []
    #             for i, driver_name in enumerate(self.list_driver):
    #                 checkBox = QtWidgets.QCheckBox(f"{driver_name}")
    #                 checkBox.setChecked(True)
    #                 self.list_checkBox.append(checkBox)
    #                 tab.setIndexWidget(sti.index(i, 0), checkBox)

    #             formLayout.addRow(QtWidgets.QLabel(""), tab)

    #             download_pushButton = QtWidgets.QPushButton()
    #             download_pushButton.clicked.connect(self.installListDriver)
    #             download_pushButton.setText("Download")
    #             formLayout.addRow(download_pushButton)

    #             centralWidget.setLayout(formLayout)

    #         def masterCheckBoxChanged(self):

    #             """ Checked all the checkBox related to the official github repo """

    #             state = self.masterCheckBox.isChecked()
    #             for checkBox in self.list_checkBox:
    #                 checkBox.setChecked(state)

    #         def closeEvent(self,event):

    #             """ This function does some steps before the window is really killed """

    #             QtWidgets.QApplication.quit()  # close the interface

    #         def installListDriver(self):

    #             """ Install all the drivers for which the corresponding checkBox has been checked """

    #             list_bool = [checkBox.isChecked() for checkBox in self.list_checkBox]

    #             list_driver_to_download = [driver_name for (driver_name, driver_bool) in zip(self.list_driver, list_bool) if driver_bool]
    #             _download_drivers(paths.DRIVER_GITHUB['official'], list_driver_to_download, OUTPUT_DIR)


    #     print("Open driver installer")
    #     app = QtWidgets.QApplication.instance()
    #     if app is None:
    #         app = QtWidgets.QApplication([])

    #     driverInstaller = DriverInstaller()
    #     driverInstaller.show()
        # app.exec_()
