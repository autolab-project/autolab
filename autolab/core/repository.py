# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 18:16:20 2023

@author: Jonathan
"""

import os
import sys
import zipfile
import tempfile
import shutil
import urllib.request
import json
from typing import Union, Tuple

from . import paths
from . import drivers
from .utilities import input_wrap
from .gitdir import download


def _format_url(url: str):
    """ Change github repo name to download link """

    if url.endswith(".zip"):
        format_url = url
    else:
        format_url = url if "/tree/" in url else url + "/tree/master"
        format_url = format_url.replace("/tree/", "/archive/refs/heads/")
        format_url += ".zip"
    return format_url


def _download_repo(url: str, output_dir: str):
    try:
        import requests
        from tqdm import tqdm
    except:
        print("Package tqdm or requests not found, can't display download progression")
        print(f"Downloading {url}")
        with urllib.request.urlopen(url) as github_repo_zip:
            with open(output_dir, 'wb') as repo_zip:
                repo_zip.write(github_repo_zip.read())
    else:
        """https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests"""
        # Streaming, so we can iterate over the response.
        response = requests.get(url, stream=True)

        # Sizes in bytes.
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024

        with tqdm(total=total_size, unit="B", unit_scale=True,
                  desc=f"Downloading {url}") as progress_bar:
            with open(output_dir, "wb") as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)

        if total_size not in (0, progress_bar.n):
            raise RuntimeError("Could not download file")


def _unzip_repo(repo_zip: str, output_dir: str):
    """ Unzip repo_zip to output_dir using a temporary folder"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    temp_dir = tempfile.mkdtemp()
    try:
        from tqdm import tqdm
    except:
        print("Package tqdm not found, can't display progression")
        with zipfile.ZipFile(repo_zip, 'r') as zip_open:
            repo_name = zip_open.namelist()[0][:-1]
            print(f'Extracting {repo_name}')
            zip_open.extractall(temp_dir)

        temp_unzip_repo = os.path.join(temp_dir, repo_name)
        print(f'Moving drivers to {output_dir}')
        for filename in os.listdir(temp_unzip_repo):
            _copy_move(temp_unzip_repo, filename, output_dir)
    else:
        """https://stackoverflow.com/questions/4341584/extract-zipfile-using-python-display-progress-percentage"""
        with zipfile.ZipFile(repo_zip, 'r') as zf:
            repo_name = str(zf.namelist()[0])[:-1]
            for member in tqdm(zf.infolist(),
                               desc=f'Extracting {repo_name}'):
                zf.extract(member, temp_dir)

        temp_unzip_repo = os.path.join(temp_dir, repo_name)
        for filename in tqdm(os.listdir(temp_unzip_repo),
                             desc=f'Moving drivers to {output_dir}'):
            _copy_move(temp_unzip_repo, filename, output_dir)

    os.rmdir(temp_unzip_repo)
    os.rmdir(temp_dir)


def _copy_move(temp_unzip_repo, filename, output_dir):
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


def _check_empty_driver_folder():
    if not os.listdir(paths.DRIVER_SOURCES['official']):
        print(f"No drivers found in {paths.DRIVER_SOURCES['official']}")
        install_drivers()


def install_drivers(*repo_url: Union[None, str, Tuple[str, str]],
                    skip_input=False, experimental_feature=False):
    """ Ask if want to install drivers from repo url.
    repo_url: can be url or tuple ('path to install', 'url to download').
    If no argument passed, download official drivers to official driver folder.
    If only url given, use official driver folder.
    Also install mandatory drivers (system, dummy, plotter) from official repo."""
    if experimental_feature:
        _install_drivers_custom()
        return None

    # Download mandatory drivers
    official_folder = paths.DRIVER_SOURCES['official']
    official_url = paths.DRIVER_REPOSITORY[official_folder]
    mandatory_drivers = ['system', 'dummy', 'plotter']

    for driver in mandatory_drivers:
        if not os.path.isdir(os.path.join(official_folder, driver)):
            print(f"Installing driver '{driver}' to {official_folder}")
            _download_driver(official_url, driver, official_folder, _print=False)

    # Ask if want to download drivers from repo_url
    temp_folder = os.environ['TEMP']  # This variable can be set in autolab_config.ini
    temp_repo_folder = tempfile.mkdtemp(dir=temp_folder)

    # create list of tuple with tuple being ('path to install', 'url to download')
    if len(repo_url) == 0:
        list_repo_tuple = list(paths.DRIVER_REPOSITORY.items())  # This variable can be modified in autolab_config.ini
    else:
        list_repo_tuple = list(repo_url)
        for i, repo_url_tmp in enumerate(list_repo_tuple):
            if isinstance(repo_url_tmp, str):
                list_repo_tuple[i] = (official_folder, repo_url_tmp)
            elif isinstance(repo_url_tmp, dict):
                raise TypeError("Error: This option has been removed, use tuple instead with (folder, url)")
            elif not isinstance(repo_url_tmp, tuple):
                raise TypeError(f'repo_url must be str or tuple. Given {type(repo_url_tmp)}')
            assert len(list_repo_tuple[i]) == 2, "Expect (folder, url), got wrong length: {len(list_repo_tuple[i])} for {list_repo_tuple[i]}"

    for repo_tuple in list_repo_tuple:
        drivers_folder, drivers_url = repo_tuple

        if r"github.com/" in drivers_url:
            repo_name = drivers_url.split(r"github.com/")[1].split("/")[1]
        else:
            repo_name = "temp_folder"

        repo_zip_url = _format_url(drivers_url)
        zip_name = "-".join((repo_name, os.path.basename(repo_zip_url)))
        temp_repo_zip = os.path.join(temp_repo_folder, zip_name)

        if skip_input: ans = 'yes'
        else:
            ans = input_wrap(f'Install drivers from {drivers_url} to {drivers_folder}? [default:yes] > ')

        if ans.strip().lower() == 'no': continue

        _download_repo(repo_zip_url, temp_repo_zip)
        _unzip_repo(temp_repo_zip, drivers_folder)
        os.remove(temp_repo_zip)
    os.rmdir(temp_repo_folder)

    # Update available drivers
    drivers.update_drivers_paths()


# =============================================================================
# Functions used to download specific driver, Not optimized to download full
# repository. Use install_drivers() instead
# =============================================================================

def _get_drivers_list_from_github(url):
    """ Returns driver list from a github repo.
    url of a repository contaning driver folders.
    """
    url_api = url

    if url_api.startswith('https://github.com'):
        url_api = url_api.replace('https://github.com', 'https://api.github.com/repos')

    if '/tree/' in url_api:
        url_api = url_api.replace("/tree/", '/git/trees/')
    else:
        url_api += '/git/trees/master'

    with urllib.request.urlopen(url_api) as f:
        html = json.load(f)

    driver_list = [tree['path'] for tree in html['tree'] if '.' not in tree['path']]
    if 'LICENSE' in driver_list:
        driver_list.remove('LICENSE')

    return driver_list

def _download_driver(url, driver_name, output_dir, _print=True):
    """ Download a driver from an github url """
    try:
        if _print:
            print(f"Downloading {driver_name}")

        driver_url = url
        if '/tree/' not in driver_url: driver_url += '/tree/master'
        driver_url = driver_url + "/" + driver_name
        # Too slow to be used for full repo, only use it for one or 2 drivers
        # 'HTTP Error 403: rate limit exceeded' due to too much download if don't have github account
        download(driver_url, output_dir=output_dir, _print=_print)
    except:  # if use Exception, crash python when having error
        e = f"Error when downloading driver '{driver_name}'"
        if _print:
            print(e, file=sys.stderr)
        else:
            return e


def _install_drivers_custom(_print=True, parent=None):
    """ Ask the user which driver to install from the official autolab driver github repo.
    If qtpy is install, open a GUI to select the driver.
    Else, prompt the user to install individual drivers. """
    official_folder = paths.DRIVER_SOURCES['official']
    official_url = paths.DRIVER_REPOSITORY[official_folder]

    try:
        list_driver = _get_drivers_list_from_github(official_url)
    except:
        print(f'Cannot access {official_url}, skip installation')
        return None

    try:
        from qtpy import QtWidgets, QtGui
    except:
        print("No qtpy installed. Using the console to install drivers instead")

        if _print:
            print(f"Drivers will be downloaded to {official_folder}")
        for driver_name in list_driver:
            ans = input(f'Download {driver_name}? [default:yes] > ')  # didn't use input_wrap because don't want to say yes to download all drivers
            if ans.strip().lower() == 'stop':
                break
            if ans.strip().lower() != 'no':
                _download_driver(official_url, driver_name, official_folder, _print=_print)
    else:

        class DriverInstaller(QtWidgets.QMainWindow):

            def __init__(self, url, list_driver, OUTPUT_DIR, parent=None):
                """ GUI to select which driver to install from the official github repo """

                self.gui = parent
                self.url = url
                self.list_driver = list_driver
                self.OUTPUT_DIR = OUTPUT_DIR

                super().__init__(parent)

                self.setWindowTitle("Autolab - Driver Installer")
                self.setFocus()
                self.activateWindow()

                self.statusBar = self.statusBar()

                centralWidget = QtWidgets.QWidget()
                self.setCentralWidget(centralWidget)

                # OFFICIAL DRIVERS
                formLayout = QtWidgets.QFormLayout()

                self.masterCheckBox = QtWidgets.QCheckBox(f"From {paths.DRIVER_REPOSITORY[paths.DRIVER_SOURCES['official']]}:")
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
                tab.horizontalHeader().setSectionResizeMode(
                    0, QtWidgets.QHeaderView.ResizeToContents)
                tab.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
                tab.setSizeAdjustPolicy(tab.AdjustToContents)

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

                centralWidget.setLayout(formLayout)

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

                if all(list_bool):  # Better for all drivers
                    install_drivers(skip_input=True, experimental_feature=False)
                    self.close()
                elif any(list_bool):  # Better for couple drivers
                    for driver_name in list_driver_to_download:
                        if _print:
                            print(f"Downloading {driver_name}")
                            # self.setStatus(f"Downloading {driver_name}", 5000)  # OPTIMIZE: currently thread blocked by installer so don't show anything until the end
                        e = _download_driver(self.url, driver_name,
                                             self.OUTPUT_DIR, _print=False)
                        if e is not None:
                            print(e, file=sys.stderr)
                            # self.setStatus(e, 10000, False)
                    self.setStatus('Finished!', 5000)

            def setStatus(self, message: str, timeout: int = 0, stdout: bool = True):
                """ Modify the message displayed in the status bar and add error message to logger """
                self.statusBar.showMessage(message, timeout)
                if not stdout: print(message, file=sys.stderr)

        if parent is None:
            if  _print: print("Open driver installer")
            app = QtWidgets.QApplication.instance()
            if app is None: app = QtWidgets.QApplication([])

        driverInstaller = DriverInstaller(
            official_url, list_driver, official_folder, parent=parent)
        driverInstaller.show()
        if parent is None: app.exec()

    # Update available drivers
    drivers.update_drivers_paths()
