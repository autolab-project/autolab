Releases notes
---------------

Development version
===================

* The help of an Element (Device approach) can be either displayed through its ``element.help()`` function or by printing the object ``print(element)``.
* The help of a Variable (Device approach) now display its python type.

(last) v1.1.6:
==============
* Addition of the driver sacher_PC500

v1.1.5:
* yokogawa_AQ6370: fix on the single function of the class Driver: it will now wait to finish the operation

v1.1.4:
* yokogawa_AQ6370: small fixes including modification of the names of communication functions (send and recv became write and read respectively)

v1.1.3:
* minor fixes
* addition of a few functions and the connection class Driver_GPIB to agilent_33220A
* addition of the driver keithley_2200

v1.1.2: fixed issue with using local config and OS command autolab driver

v1.1.1: fixed installation issue regarding version.txt

v1.1
====

Core:

* autolab.help() renamed in autolab.doc()
* Functions get_driver_by_config and get_device_by_config have been deleted. Use get_driver or get_device functions to load an instrument either with its full configuration or with a local configuration.
* The methods of a Driver instance can be listed through the function autolab.explore_driver(instance).
* New function autolab.infos() that displays the available drivers and local configurations in the system.
* The local configurations are now refered as 'local_config' in the functions of autolab.
* The OS shell interface has been completely restructured. Most of the features of Autolab are now available (doc, report, infos, drivers, devices, gui..) through a unique command 'autolab'.
* Added trigger for statistics of use (can be disabled).

Drivers:

* The driver category is now stored in the script <driver>_utilities.py in the same folder (previously <driver>_parser.py).
* exfo_PM1613: 1) Driver update taking into account that the power meter returns ***** when changing its scale. 2) typos in the type of power of get_driver_model (str -> float).
* Modification of the way we pass argument to socket.send function. Safer now as we explicitely convert the argument to a string (impacted a few instruments that use socket module such as yokogawa_AQ6370, etc.).

Help:

* Efforts to merge all the helps [in python, OS (autolab driver/device), etc.] to a common standard, using the very same functions.

v1.0
=====

* First push
