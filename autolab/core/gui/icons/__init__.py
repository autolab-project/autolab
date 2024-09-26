# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 16:02:35 2024

@author: Jonathan
"""
from typing import Dict, Union
import os

from qtpy import QtWidgets, QtGui

ICONS_FOLDER = os.path.dirname(__file__)
standardIcon = QtWidgets.QApplication.style().standardIcon


def format_icon_path(name: str) -> str:
    return os.path.join(ICONS_FOLDER, name).replace("\\", "/")


def create_icon(name: str) -> QtGui.QIcon:
    return QtGui.QIcon(format_icon_path(name))


def create_pixmap(name: str) -> QtGui.QPixmap:
    return QtGui.QPixmap(format_icon_path(name))


icons: Dict[str, Union[QtGui.QIcon, QtGui.QPixmap, standardIcon]] = {
    'action': create_icon('action-icon.svg'),
    'add': create_icon('add-icon.svg'),
    'autolab': create_icon('autolab-icon.ico'),
    'autolab-pixmap': create_pixmap('autolab-icon.ico'),
    'config': create_icon('config-icon.svg'),
    'copy': create_icon('copy-icon.svg'),
    'disconnect': create_icon('disconnect-icon.svg'),
    'down': create_icon('down-icon.svg'),
    'export': create_icon('export-icon.svg'),
    'file': standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView),
    'folder': standardIcon(QtWidgets.QStyle.SP_DirIcon),
    'github': create_icon('github-icon.svg'),
    'import': create_icon('import-icon.svg'),
    'is-disable': create_icon('is-enable-icon.svg'),
    'is-enable': create_icon('is-enable-icon.svg'),
    'measure': create_icon('measure-icon.svg'),
    'monitor': create_icon('monitor-icon.svg'),
    'parameter': create_icon('parameter-icon.svg'),
    'paste': create_icon('paste-icon.svg'),
    'pdf': create_icon('pdf-icon.svg'),
    'plotter': create_icon('plotter-icon.svg'),
    'preference': create_icon('preference-icon.svg'),
    'read-save': create_icon('read-save-icon.svg'),
    'readthedocs': create_icon('readthedocs-icon.svg'),
    # 'recipe': create_icon('recipe-icon.svg'),
    'redo': create_icon('redo-icon.svg'),
    'reload': standardIcon(QtWidgets.QStyle.SP_BrowserReload),
    'remove': create_icon('remove-icon.svg'),
    'rename': create_icon('rename-icon.svg'),
    'scanner': create_icon('scanner-icon.svg'),
    'slider': create_icon('slider-icon.svg'),
    'undo': create_icon('undo-icon.svg'),
    'up': create_icon('up-icon.svg'),
    'variables': create_icon('variables-icon.svg'),
    'write': create_icon('write-icon.svg'),
}

icons.update({
    'int': create_icon('int-icon.svg'),
    'float': create_icon('float-icon.svg'),
    'str': create_icon('str-icon.svg'),
    'bytes': create_icon('bytes-icon.svg'),
    'bool': create_icon('bool-icon.svg'),
    'tuple': create_icon('tuple-icon.svg'),
    'ndarray': create_icon('ndarray-icon.svg'),
    'DataFrame': create_icon('dataframe-icon.svg'),
})
