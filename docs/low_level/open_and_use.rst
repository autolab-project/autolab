.. _userguide_low:

Load and use a Driver
=====================

The low-level interface provides a raw access to the drivers implemented in Autolab, through a **Driver** object, which contains functions that perform particular operations in your instrument.

.. attention::

	The Autolab drivers may contains internal functions, that are not dedicated to be called by the user, and some functions requires particular types of inputs. **The authors declines any responsibility for the consequences of an incorrect use of the drivers**. To avoid any problems, make sure you have a real understanding of what you are doing, or prefer the use of the :ref:`highlevel`.
	
To see the list of available drivers in Autolab, call the ``list_drivers`` function.

.. code-block:: python

	>>> import autolab
	>>> autolab.list_drivers()

.. note::

	The driver of your instrument is missing ? Please contribute to Autolab by creating yourself a new driver, following the provided guidelines : :ref:`create_driver`
	
Load and close a Driver
-----------------------



The instantiation of a *Driver* object is done through the function ``get_driver`` of Autolab, and requires a particular configuration: 

* The name of the driver: one of the name appearing in the ``list_drivers`` function (ex: 'yenista_TUNICS').
* The connection parameters as keywords arguments: the connection type to use to communicate with the instrument ('VISA', 'TELNET', ...), the address, the port, the slots, ...

.. code-block:: python

	>>> laserSource = autolab.get_driver('yenista_TUNICS','VISA',address='GPIB0::12::INSTR')
	
To know what is the required configuration to interact with a given instrument, call the function ``config_help`` with the name of the driver.

.. code-block:: python

	>>> autolab.config_help('yenista_TUNICS')
	
To avoid having to provide each time the full configuration of an instrument to load a **Driver** (as above), Autolab proposes to store locally this configuration. To learn more about this, please see the section :ref:`local_config`. You can then just provide the configuration name in the function ``get_driver``.

.. code-block:: python

	>>> laserSource = autolab.get_driver('my_tunics')
	
.. note::

	You can overwrite temporarily some of the parameters values of a configuration by simply providing them as keywords arguments in the ``get_driver`` function:
	
	.. code-block:: python	
		>>> laserSource = autolab.get_driver('my_tunics',address='GPIB::9::INSTR')
			
To close properly the connection to the instrument, simply call its the function ``close`` of the **Driver**. 

.. code-block:: python

	>>> lightSource.close()

Use a Driver
------------

You are now ready to use the functions implemented in the **Driver**:

.. code-block:: python

	>>> laserSource.set_wavelength(1550)
	>>> laserSource.get_wavelength()
	1550
	
You can get the list of the available functions by calling the function ``autolab.explore_driver`` with the instance of your **Driver**. Once again, note that some of these functions are note supposed to be used directly, some of them may be internal functions. 

	>>> autolab.explore_driver(laserSource)


.. _name_pythonscript_example:

Script example
--------------

With all these commands, you can now create your own Python script. Here is an example of a script that sweep the wavelength of a light source, and measure a power of a power meter:

.. code-block:: python
	
	# Import the package
	import autolab
	import pandas
	
	# Open the Devices
	myTunics = autolab.get_driver('my_tunics')
	myPowerMeter = autolab.get_driver('my_power_meter')
	
	# Turn on the light source
	myTunics.set_output(True)
	
	# Sweep its wavelength and measure a power with a power meter
	df = pd.DataFrame()
	for wl in range(1550,1560,0.01) :
	
	    # Set the parameter
	    myTunics.set_wavelength(wl)
	    
	    # Measures the values
	    wl_measured = myTunics.get_wavelength()
	    power = myPowerMeter.line1.set_power()
	    
	    # Store the values in a list
	    df = df.append({'wl_measured':wl_measured, 'power':power},ignore_index=True)
	
	# Turn off the light source
	myTunics.set_output(False)
	
	# Close the Devices
	myTunics.close()
	myPowerMeter.close()	
	
	# Save data
	df.to_csv('data.csv')
