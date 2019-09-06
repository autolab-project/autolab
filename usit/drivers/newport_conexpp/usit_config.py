# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""

def configure(devDriver,devUsit):

    
    for subName,subDriver in [('tic',devDriver.tic),('tac',devDriver.tac)] :
    
        subDevUsit = devUsit.addModule(subName)             
        
        subDevUsit.addVariable('velocity',
                            setFunction=subDriver.setVelocity,
                            getFunction=subDriver.getVelocity)
        
        subDevUsit.addVariable('acceleration',
                            setFunction=subDriver.setAcceleration,
                            getFunction=subDriver.getAcceleration)
        
        subDevUsit.addVariable('angle',
                            setFunction=subDriver.setAngle,
                            getFunction=subDriver.getAngle)
        
        subDevUsit.addVariable('transmission',
                            setFunction=subDriver.setTransmission,
                            getFunction=subDriver.getTransmission)
        
        subDevUsit.addVariable('calibrationFunction',
                               setFunction=subDriver.setCalibrationGetPowerFunction)
            
        subDevUsit.addAction('setMin',
                          function=subDriver.setMin)
        
        subDevUsit.addAction('setMax',
                          function=subDriver.setMax)
        
        subDevUsit.addAction('goHome',
                          function=subDriver.goHome)
        
        subDevUsit.addAction('calibrate',
                      function=subDriver.calibrate)
        
    
    
    