.. _userguide_low:

Open and use a driver
=====================

The low-level interface provides a raw access to instantiate and use directly a driver implemented in Autolab.

To see the list of available drivers sorted by categories, simply use the function `show_drivers` of Autolab. If you just want the list, call the `list_drivers` function.

.. code-block:: python

	>>> import autolab
	>>> autolab.show_drivers()
	>>> autolab.list_drivers()

.. note::

	The driver of your instrument is missing ? Please contribute to Autolab by creating yourself a new driver, following the provided guidelines : :ref:`create_driver`
	
To get more information about one particular available driver (connection types, modules, required configuration,...), call the function `driver_help` of Autolab, with the name of the driver.

.. code-block:: python

	>>> autolab.driver_help('yenista_TUNICS')

* A :ref:`lowlevel`, which provides a raw access to the package's drivers functions. The instantiation of a **Driver** requires some configuration information (ex `yenista_TUNICS` here) that can be saved locally to simplify the user scripts (ex `my_powermeter` here).

