# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""


from .config import config as _config

if _config.checkConfig() is True :
    _config = _config.getConfig()
    from .devices.devices import deviceManager as devices
    from .recorder_old.recorder import Recorder, Recorder_V2