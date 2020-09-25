# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:26:32 2019

@author: qchat
"""

from PyQt5 import QtCore

class ThreadManager :
    
    """ This class is dedicated to manage the different threads, 
    from their creation, to their deletion them after they have been used """
    
    
    def __init__(self,gui):
        self.gui = gui
        self.threads = {}
        
        
        
    def start(self,item,intType,value=None):
        
        """ This function is called when a new thread is requested, 
        for a particular intType interaction type """
        
        # GUI disabling
        self.gui.tree.setEnabled(False)
        
        # Status writing
        if intType == 'read' : status = f'Reading {item.variable.address()}...'
        elif intType == 'write' : status = f'Writing {item.variable.address()}...'
        elif intType == 'execute' : status = f'Executing {item.action.address()}...'
        self.gui.setStatus(status)

        # Thread configuration
        thread = InteractionThread(item,intType,value)
        tid = id(thread)
        self.threads[tid] = thread
        thread.endSignal.connect(lambda error, x=tid : self.threadFinished(x,error))
        thread.finished.connect(lambda x=tid : self.delete(x))
        
        # Starting thread
        thread.start()
        
        
    def threadFinished(self,tid,error):
        
        """ This function is called when a thread has finished its job, with an error or not 
        It uptates the status bar of the GUI in consequence and enabled back the GUI"""
        
        if error is None : self.gui.clearStatus()
        else : self.gui.setStatus(str(error))
        
        self.gui.tree.setEnabled(True)
        
        
        
    def delete(self,tid):
        
        """ This function is called when a thread is about to be deleted. 
        This removes it from the dictionnary self.threads, for a complete deletion """
        
        self.threads.pop(tid)
        
        
        
        
        
        
class InteractionThread(QtCore.QThread):
    
    """ This class is dedicated to operation interaction with the devices, in a new thread """
    
    endSignal = QtCore.pyqtSignal(object)
    
    
    def __init__(self,item,intType,value):
        QtCore.QThread.__init__(self)
        self.item = item
        self.intType = intType
        self.value = value
        
        
        
    def run(self):
        
        """ Depending on the interaction type requested, this function reads or writes a variable, 
        or execute an action. """
        
        error = None
        
        try :
            if self.intType == 'read' : self.item.variable()
            elif self.intType == 'write' : 
                self.item.variable(self.value)
                if self.item.variable.readable : self.item.variable()
            elif self.intType == 'execute' : 
                if self.value is not None :
                    self.item.action(self.value)
                else :
                    self.item.action()
            
        except Exception as e:
            error = e
        self.endSignal.emit(error)
       
        