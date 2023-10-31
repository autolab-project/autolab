
import sys
import os

# This driver is a copy of the ct400 driver using the ct440 option, and serves as a proxy for the ct440 driver.

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # To get access to yenista_CT400

category = 'All-band Optical Component Tester'

from yenista_CT400.yenista_CT400_utilities import Driver_parser
