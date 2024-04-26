# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 20:13:46 2024

@author: jonathan
"""


from qtpy import QtWidgets

from ..config import get_GUI_config


def get_font_size() -> int:
    GUI_config = get_GUI_config()
    if GUI_config['font_size'] != 'default':
        font_size = int(GUI_config['font_size'])
    else:
        font_size = QtWidgets.QApplication.instance().font().pointSize()
        return font_size


def setLineEditBackground(obj, state: str, font_size: int = None):
    """ Sets background color of a QLineEdit widget based on its editing state """
    if state == 'synced': color='#D2FFD2' # vert
    if state == 'edited': color='#FFE5AE' # orange

    if font_size is None:

        obj.setStyleSheet(
            "QLineEdit:enabled {background-color: %s}" % (
                color))
    else:
        obj.setStyleSheet(
            "QLineEdit:enabled {background-color: %s; font-size: %ipt}" % (
                color, font_size))
