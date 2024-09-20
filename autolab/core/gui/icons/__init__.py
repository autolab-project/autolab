# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 16:02:35 2024

@author: Jonathan
"""
import os

icons_folder = os.path.dirname(__file__)


ACTION_ICON_NAME = os.path.join(icons_folder, 'action-icon.svg').replace("\\", "/")
ADD_ICON_NAME = os.path.join(icons_folder, 'add-icon.svg').replace("\\", "/")
AUTOLAB_ICON_NAME = os.path.join(icons_folder, 'autolab-icon.ico').replace("\\", "/")
CONFIG_ICON_NAME = os.path.join(icons_folder, 'config-icon.svg').replace("\\", "/")
DISCONNECT_ICON_NAME = os.path.join(icons_folder, 'disconnect-icon.svg').replace("\\", "/")
DOWN_ICON_NAME = os.path.join(icons_folder, 'down-icon.svg').replace("\\", "/")
EXPORT_ICON_NAME = os.path.join(icons_folder, 'export-icon.svg').replace("\\", "/")
GITHUB_ICON_NAME = os.path.join(icons_folder, 'github-icon.svg').replace("\\", "/")
IMPORT_ICON_NAME = os.path.join(icons_folder, 'import-icon.svg').replace("\\", "/")
IS_DISABLE_ICON_NAME = os.path.join(icons_folder, 'is-disable-icon.svg').replace("\\", "/")
IS_ENABLE_ICON_NAME = os.path.join(icons_folder, 'is-enable-icon.svg').replace("\\", "/")
MEASURE_ICON_NAME = os.path.join(icons_folder, 'measure-icon.svg').replace("\\", "/")
MONITOR_ICON_NAME = os.path.join(icons_folder, 'monitor-icon.svg').replace("\\", "/")
PARAMETER_ICON_NAME = os.path.join(icons_folder, 'parameter-icon.svg').replace("\\", "/")
PDF_ICON_NAME = os.path.join(icons_folder, 'pdf-icon.svg').replace("\\", "/")
PLOTTER_ICON_NAME = os.path.join(icons_folder, 'plotter-icon.svg').replace("\\", "/")
PREFERENCE_ICON_NAME = os.path.join(icons_folder, 'preference-icon.svg').replace("\\", "/")
READ_SAVE_ICON_NAME = os.path.join(icons_folder, 'read-save-icon.svg').replace("\\", "/")
READTHEDOCS_ICON_NAME = os.path.join(icons_folder, 'readthedocs-icon.svg').replace("\\", "/")
RECIPE_ICON_NAME = os.path.join(icons_folder, 'recipe-icon.svg').replace("\\", "/")
REDO_ICON_NAME = os.path.join(icons_folder, 'redo-icon.svg').replace("\\", "/")
REMOVE_ICON_NAME = os.path.join(icons_folder, 'remove-icon.svg').replace("\\", "/")
RENAME_ICON_NAME = os.path.join(icons_folder, 'rename-icon.svg').replace("\\", "/")
SCANNER_ICON_NAME = os.path.join(icons_folder, 'scanner-icon.svg').replace("\\", "/")
SLIDER_ICON_NAME = os.path.join(icons_folder, 'slider-icon.svg').replace("\\", "/")
UNDO_ICON_NAME = os.path.join(icons_folder, 'undo-icon.svg').replace("\\", "/")
UP_ICON_NAME = os.path.join(icons_folder, 'up-icon.svg').replace("\\", "/")
WRITE_ICON_NAME = os.path.join(icons_folder, 'write-icon.svg').replace("\\", "/")


icons = {'action': ACTION_ICON_NAME,
         'add': ADD_ICON_NAME,
         'autolab': AUTOLAB_ICON_NAME,
         'config': CONFIG_ICON_NAME,
         'disconnect': DISCONNECT_ICON_NAME,
         'down': DOWN_ICON_NAME,
         'export': EXPORT_ICON_NAME,
         'github': GITHUB_ICON_NAME,
         'import': IMPORT_ICON_NAME,
         'is-disable': IS_DISABLE_ICON_NAME,
         'is-enable': IS_ENABLE_ICON_NAME,
         'measure': MEASURE_ICON_NAME,
         'monitor': MONITOR_ICON_NAME,
         'parameter': PARAMETER_ICON_NAME,
         'pdf': PDF_ICON_NAME,
         'plotter': PLOTTER_ICON_NAME,
         'preference': PREFERENCE_ICON_NAME,
         'read-save': READ_SAVE_ICON_NAME,
         'readthedocs': READTHEDOCS_ICON_NAME,
         'recipe': RECIPE_ICON_NAME,
         'redo': REDO_ICON_NAME,
         'remove': REMOVE_ICON_NAME,
         'rename': RENAME_ICON_NAME,
         'scanner': SCANNER_ICON_NAME,
         'slider': SLIDER_ICON_NAME,
         'undo': UNDO_ICON_NAME,
         'up': UP_ICON_NAME,
         'write': WRITE_ICON_NAME,
         }


INT_ICON_NAME = os.path.join(icons_folder, 'int-icon.svg').replace("\\", "/")
FLOAT_ICON_NAME = os.path.join(icons_folder, 'float-icon.svg').replace("\\", "/")
STR_ICON_NAME = os.path.join(icons_folder, 'str-icon.svg').replace("\\", "/")
BYTES_ICON_NAME = os.path.join(icons_folder, 'bytes-icon.svg').replace("\\", "/")
BOOL_ICON_NAME = os.path.join(icons_folder, 'bool-icon.svg').replace("\\", "/")
TUPLE_ICON_NAME = os.path.join(icons_folder, 'tuple-icon.svg').replace("\\", "/")
NDARRAY_ICON_NAME = os.path.join(icons_folder, 'ndarray-icon.svg').replace("\\", "/")
DATAFRAME_ICON_NAME = os.path.join(icons_folder, 'dataframe-icon.svg').replace("\\", "/")


icons.update({
'int': INT_ICON_NAME,
'float': FLOAT_ICON_NAME,
'str': STR_ICON_NAME,
'bytes': BYTES_ICON_NAME,
'bool': BOOL_ICON_NAME,
'tuple': TUPLE_ICON_NAME,
'ndarray': NDARRAY_ICON_NAME,
'DataFrame': DATAFRAME_ICON_NAME,
})
