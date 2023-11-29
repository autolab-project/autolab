# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 14:48:14 2017

@author: Quentin Chateiller
quentin.chateiller@c2n.upsaclay.fr


"""
#from threading import Event, Thread

#started = Event()

#def gui() :
#
#    if started.is_set():
#        print("Gui already running")
#    else :
#        t=AppThread()
#        t.start()


def start():
    """ Open the Autolab GUI """

    import os
    from ..config import get_GUI_config
    GUI_config = get_GUI_config()
    if GUI_config["QT_API"] != "default":
        os.environ['QT_API'] = str(GUI_config["QT_API"])
    try:
        from qtpy import QtWidgets
        import pyqtgraph
    except ModuleNotFoundError:
        print("""Packages missing to use the GUI. You need to install qtpy, \
              pyqtgraph and one of PyQt5, PySide2, PyQt6 or PySide6.

              Using pip:
              pip install qtpy
              pip install pyqtgraph
              pip install PyQt5
              pip install PySide2
              pip install PyQt6
              pip install PySide6

              Using anaconda:
              conda install qtpy
              conda install pyqtgraph
              conda install pyqt
              conda install -c conda-forge pyside2
              no PyQt6 anaconda version available
              conda install -c conda-forge pyside6
              """) # TODO: check if need matplotlib once done with pyqtgraph conversion
    else:
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])

        from .controlcenter.main import ControlCenter
        gui = ControlCenter()
        gui.initialize()
        gui.show()
        app.exec()


#class AppThread(Thread):
#
#    def __init__(self):
#
#        Thread.__init__(self)
#
#    def run(self):
#
#        started.set()
#
#        _run()
#
#        started.clear()
#
