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


def gui():
    """ Open the Autolab GUI """
    _start('main')


def plotter():
    """ Open the Autolab Plotter """
    _start('plotter')


def monitor(var):
    """ Open the Autolab Monitor for variable var """
    from .variables import Variable

    class temp: pass
    name = var.name if isinstance(var, Variable) else 'Variable'
    item = temp()
    item.variable = Variable(name, var)
    _start('monitor', item=item)


def  add_device():
    """ Open the utility to add a device """
    _start('add_device')


def _start(gui: str, **kwargs):
    """ Open the Autolab GUI if gui='main', the Plotter if gui='plotter'
    or the Monitor if gui='monitor' """

    import os
    from ..config import get_GUI_config
    GUI_config = get_GUI_config()
    if GUI_config['QT_API'] != 'default':
        os.environ['QT_API'] = str(GUI_config['QT_API'])
    try:
        import pyqtgraph as pg
        from qtpy import QtWidgets
    except ModuleNotFoundError as e:
        print(f"""Can't use GUI, package(s) missing: {e}
Need to install pyqtgraph, qtpy, and one of PyQt5, PySide2, PyQt6 or PySide6.

Using pip:
pip install pyqtgraph
pip install qtpy
pip install PyQt5
pip install PySide2
pip install PyQt6
pip install PySide6

Using anaconda:
conda install pyqtgraph
conda install qtpy
conda install pyqt
conda install -c conda-forge pyside2
no PyQt6 anaconda version available
conda install -c conda-forge pyside6
""")
    else:
        background = GUI_config['image_background']
        foreground = GUI_config['image_foreground']
        pg.setConfigOptions(background=background, foreground=foreground)
        pg.setConfigOption('imageAxisOrder', 'row-major')

        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])

        if GUI_config['font_size'] != 'default':
            font = app.font()
            font.setPointSize(int(GUI_config['font_size']))
            app.setFont(font)

        if gui == 'main':
            from .controlcenter.main import ControlCenter
            gui = ControlCenter()
            gui.initialize()
        elif gui == 'plotter':
            from .plotting.main import Plotter
            gui = Plotter(None)
        elif gui == 'monitor':
            from .monitoring.main import Monitor
            item = kwargs.get('item')
            gui = Monitor(item)
        elif gui == 'add_device':
            from .controlcenter.main import addDeviceWindow
            gui = addDeviceWindow()
        else:
            raise ValueError(f"gui accept either 'main', 'plotter', 'monitor' or 'add_device', given {gui}")
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
