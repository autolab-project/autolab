.. _extra:

Experimental features
=====================

Plot from driver
################

When creating a plot from a driver inside the GUI, Python usually crashes because the created plot isn't connected to the GUI thread.
To avoid this issue, a driver can put gui=None as an argument and use the command gui.createWidget to ask the GUI to create the widget and send back the instance.
This solution can be used to create and plot data in a custom widget while using the GUI.
