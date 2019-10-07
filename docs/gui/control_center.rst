Control panel
=============

The Autolab GUI Control Panel provides an easy way to control your instruments. From it, you can visualize and set the value of its *Variables*, and execute its *Action* through graphical widgets. 

Devices tree
------------

The name of each *Device* configured in Autolab is represented in a tree widget. If the connection to a given instrument is not already established, a click on the associated *Device* will establish this connection. The corresponding *Element* hierarchy of this *Device* then appears. 

Actions
#######

A button **Execute** is present in each *Action* line. Clicking the button executes the associated action.




Variables
#########

The value of a *Variable* can be set or read if its type is numerical (integer, float or boolean). 

If the *Variable* is readable (read function provided in the driver), a **Read** button is available on its line. When clicking on this button, the *Variable*'s value is read and displayed in a line edit widget (integer / float values) or in a checkbox (boolean). 

If the *Variable* is writable (write function provided in the driver), its value can be edited and sent to the instrument (return pressed for interger / float values, check box checked or unchecked for boolean values).

To read and save the value of a *Variable*, right click on its line and select **Read and save as...**. You will be prompted to select the path of the output file. 


Monitoring
----------

A readable and numerical *Variable* can be monitored in time. To start the monitoring of this *Variable*, right click on it and select **Start monitoring**. Please visit the section 
:ref:`monitoring`. 

Scanning
--------

You can open the scanning interface with the associated button in the menu bar of the control panel window.
To configure a scan, please visit the section :ref:`scanning`. 











