.. _highlevel:

Devices (High-level interface)
==============================

What is a Device ?
------------------

The high-level interface of Autolab is an abstraction layer of its low-level interface, which allows to communicate easily and safely with laboratory instruments without knowing the structure of its associated **Driver**.

In this approach, an instrument is fully described with a hierarchy of three particular **Elements**: the **Modules**, the **Variables** and the **Actions**.

* A **Module** is an **Element** that consists in a group of **Variables**, **Actions**, and sub-**Modules**. The top-level **Module** of an instrument is called a **Device**.

* A **Variable** is an **Element** that refers to a physical quantity, whose the value can be either set and/or read from an instrument (wavelength of an optical source, position of a linear stage, optical power measured with a power meter, spectrum measured with a spectrometer...). Depending on the nature of the physical quantity, it may have a unit.

* An **Action** is an **Element** that refers to a particular operation that can be performed by an instrument. (homing of a linear stage, the zeroing of a power meter, the acquisition of a spectrum with a spectrometer...). An **Action** may have a parameter.

The **Device** of a simple instrument is usually represented by only one **Module**, and a few **Variables** and **Actions** attached to it.

.. code-block:: python

	-- Tunics (Module/Device)
		|-- Wavelength (Variable)
		|-- Output state (Variable)

Some instruments are a bit more complex, in the sense that they can host several different modules. Their representation in this interface generally consists in one top level **Module** (the frame) and several others sub-**Modules** containing the **Variables** and **Actions** of each associated modules.

.. code-block:: python

	-- XPS Controller (Module/Device)
		|-- ND Filter (Module)
			|-- Angle (Variable)
			|-- Transmission (Variable)
			|-- Homing (Action)
		|-- Linear stage (Module)
			|-- Position (Variable)
			|-- Homing (Action)		
			
This hierarchy of **Elements** is implemented for each instrument in its drivers files, and is thus ready to use.

Load and close a Device
-----------------------

The procedure to load a **Device** is the same as for the **Driver**, but with the function ``get_device``. You can provide either the name of a driver with its full configuration, or the name of a local configuration (see :ref:`local_config`).

.. code-block:: python

	>>> laserSource = autolab.get_device('yenista_TUNICS', connection='VISA', address='GPIB0::12::INSTR')
	>>> lightSource = autolab.get_device('my_tunics')
	
.. note::

	You can overwrite temporarily some of the parameters values of a configuration by simply providing them as keywords arguments in the ``get_device`` function:
	
	.. code-block:: python	
		>>> laserSource = autolab.get_device('my_tunics',address='GPIB::9::INSTR')
			
To close properly the connection to the instrument, simply call its the function ``close`` of the **Device**. This object will not be usable anymore.

.. code-block:: python

	>>> lightSource.close()
	
Navigation and help in a Device
-------------------------------

The navigation in the hierarchy of **Elements** of a given **Device** is based on relative attributes. For instance, to access the **Variable** ``wavelength`` of the **Module** (**Device**) ``my_tunics``, simply execute the following command:

.. code-block:: python

	>>> lightSource.wavelength
	
In the case of a more complex **Device**, for instance a power meter named ``my_power_meter`` that has several channels, you can access the **Variable** ``power`` of the first channel ``channel1`` with the following command:

.. code-block:: python

	>>> powerMeter = autolab.get_device('my_power_meter')
	>>> powerMeter.channel1.power
	
Every **Element** in Autolab is provided with a function ``help`` that can be called to obtain some information about it, but also to know which further **Elements** can be accessed through it, in the case of a **Module**. For a **Variable**, it will display its read and/or write functions (from the driver) and its unit if provided in the driver. For an **Action**, il will display the associated function in the driver, and its parameter if it have one.

.. code-block:: python

	>>> lightSource.help()
	>>> lightSource.wavelength.help()
	>>> powerMeter.help()
	>>> powerMeter.channel1.help()
	>>> powerMeter.channel1.power.help()

Use a Variable
--------------

If a **Variable** is readable (read function provided in the driver), its current value can be read by calling its attribute:

.. code-block:: python

	>>> lightSource.wavelength()
	1550.55
	>>> lightSource.output()
	False

If a **Variable** is writable (write function provided in the driver), its current value can be set by calling its attribute with the desired value:

.. code-block:: python

	>>> lightSource.wavelength(1549)
	>>> lightSource.output(True)
	
To save locally the value of a readable **Variable**, use its function `save` with the path of the desired output directory (default filename), or file:

.. code-block:: python

	>>> lightSource.wavelength.save('.\mesures\')
	>>> lightSource.wavelength.save('.\mesures\power.txt')

Use an Action
-------------

You can execute an **Action** simply by calling its attribute:

.. code-block:: python

	>>> linearStage = autolab.get_device('my_linear_stage')
	>>> linearStage.goHome()
	
	
Script example
--------------

With all these commands, you can now create your own Python script. Here is an example of a script that sweep the wavelength of a light source, and measure a power of a power meter:

.. code-block:: python
	
	# Import the package
	import autolab
	import pandas
	
	# Open the Devices
	myTunics = autolab.get_device('my_tunics')
	myPowerMeter = autolab.get_device('my_power_meter')
	
	# Turn on the light source
	myTunics.output(True)
	
	# Sweep its wavelength and measure a power with a power meter
	df = pd.DataFrame()
	for wl in range(1550,1560,0.01) :
	
	    # Set the parameter
	    myTunics.wavelength(wl)
	    
	    # Measures the values
	    wl_measured = myTunics.wavelength()
	    power = myPowerMeter.line1.power()
	    
	    # Store the values in a list
		df = df.append({'wl_measured':wl_measured, 'power':power},ignore_index=True)
	
	# Turn off the light source
	myTunics.output(False)
	
	# Close the Devices
	myTunics.close()
	myPowerMeter.close()	
	
	# Save data
	df.to_csv('data.csv')



