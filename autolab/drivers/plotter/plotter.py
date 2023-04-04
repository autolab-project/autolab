# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 21:26:10 2022

@author: jonathan
"""

from autolab.core.gui.plotting.analyze import *
from autolab.core.gui.plotting.analyze import AnalyzeManager as Driver

# TODO: see if Autolab Plotter should use the same driver instance (like for ct400GUI) or a seperate one (currently that)
# I think seperate is better because plotting data should not change anything to any driver and mess up with a scanner recipe.
# To use plotter functions in recipe, should use this driver that is seperate from the GUI.

class Driver_DEFAULT(Driver):
    def __init__(self):

        Driver.__init__(self)
