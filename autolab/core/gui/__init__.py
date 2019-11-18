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
    
    from PyQt5 import QtWidgets
    
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    
    from .controlcenter.main import ControlCenter
    gui = ControlCenter()
    gui.initialize()
    gui.show()
    app.exec_()
        
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
            