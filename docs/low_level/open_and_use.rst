.. _userguide_low:

Load and use a Driver
=====================

The low-level interface provides a raw access to the drivers implemented in Autolab, through a **Driver** object, which contains functions that perform particular operations in your instrument.

.. attention::

	Autolab drivers may contain internal functions, that are not dedicated to be called by the user, and some functions requires particular types of inputs. **The authors decline any responsibility for the consequences of an incorrect use of the drivers**. To avoid any problems, make sure you have a real understanding of what you are doing, or prefer the use of the :ref:`highlevel`.

To see the list of available drivers in Autolab, call the ``list_drivers`` function.

.. code-block:: python

	>>> import autolab
	>>> autolab.list_drivers()

.. note::

	The driver of your instrument is missing? Please contribute to Autolab by creating yourself a new driver, following the provided guidelines : :ref:`create_driver`

Load and close a Driver
-----------------------



The instantiation of a *Driver* object is done using the ``get_driver`` function of Autolab, and requires a particular configuration:

* The name of the driver: one of the name appearing in the ``list_drivers`` function (ex: 'yenista_TUNICS').
* The connection parameters as keywords arguments: the connection type to use to communicate with the instrument ('VISA', 'TELNET', ...), the address, the port, the slots, ...

.. code-block:: python

	>>> laserSource = autolab.get_driver('yenista_TUNICS', 'VISA', address='GPIB0::12::INSTR')

To know what is the required configuration to interact with a given instrument, call the ``config_help`` function with the name of the driver.

.. code-block:: python

	>>> autolab.config_help('yenista_TUNICS')

To close properly the connection to the instrument, simply call the ``close`` function of the **Driver**.

.. code-block:: python

	>>> lightSource.close()

Use a Driver
------------

You are now ready to use the functions implemented in the **Driver**:

.. code-block:: python

	>>> laserSource.set_wavelength(1550)
	>>> laserSource.get_wavelength()
	1550

You can get the list of the available functions by calling the ``autolab.explore_driver`` function with the instance of your **Driver**. Once again, note that some of these functions are not supposed to be used directly, some of them may be internal functions.

	>>> autolab.explore_driver(laserSource)


.. _name_pythonscript_example:

Script example
--------------

With all these commands, you can now create your own Python script. Here is an example of a script that sweep the wavelength of a light source, and measure the power of a power meter:

.. code-block:: python

	# Import the package
	import autolab
	import pandas as pd

	# Open the Devices
	myTunics = autolab.get_driver('yenista_TUNICS', connection='VISA', address='GPIB0::12::INSTR')
	myPowerMeter = autolab.get_driver('powermeter_driver', connection='DLL')

	# Turn on the light source
	myTunics.set_output(True)

	# Sweep its wavelength and measure a power with a power meter
	df = pd.DataFrame()
	step = 0.01
	start = 1550
	stop = 1560
	points = int(1 + (stop - start)/step)
	for wl in np.linspace(start, stop, points):

	    # Set the parameter
	    myTunics.set_wavelength(wl)

	    # Measures the values
	    wl_measured = myTunics.get_wavelength()
	    power = myPowerMeter.line1.get_power()

	    # Store the values in a list
	    df = df.append({'wl_measured': wl_measured, 'power': power}, ignore_index=True)

	# Turn off the light source
	myTunics.set_output(False)

	# Close the Devices
	myTunics.close()
	myPowerMeter.close()

	# Save data
	df.to_csv('data.csv')
