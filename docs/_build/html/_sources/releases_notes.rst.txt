Releases notes
---------------

Development version
===================

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
* exfo_PM1613: Driver update taking into account that the power meter returns ***** when changing its scale. 
* yokogawa_...
* Other driver update


v1.0
=====

* First push
