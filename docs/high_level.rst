.. _highlevel:

High-level interface (Devices)
==============================

What is a Device ?
------------------

The high-level interface of Autolab is an abstraction layer of its low-level interface, which allows to communicate easily with laboratory instruments without knowing the structure of its associated **Driver**.

In this approach, an instrument is fully described with a hierarchy of three particular **Elements**: the **Modules**, the **Variables** and the **Actions**.

* A **Module** is an **Element** that consists in a group of **Variables**, **Actions**, and sub-**Modules**. The top-level **Module** of an instrument is called a **Device**.

* A **Variable** is an **Element** that refers to a physical quantity, whose the value can be either set and/or read from an instrument (wavelength of an optical source, position of a linear stage, optical power measured with a power meter, spectrum measured with a spectrometer...). Depending on the nature of the physical quantity, it may have a unit.

* An **Action** is an **Element** that refers to a particular operation that can be performed by an instrument. (homing of a linear stage, the zeroing of a power meter, the acquisition of a spectrum with a spectrometer...). An **Action** may have a parameter.

A simple instrument is usually composed of only one **Module** (a **Device**), and a few **Variables** and **Actions** attached to it.

.. code-block:: python

	-- Tunics (Module/Device)
		|-- Wavelength (Variable)
		|-- Output state (Variable)
	

Some instruments are a bit more complex, in the sense that they can host several different modules. Their representation in this interface generally consists in one top level **Module** (the frame, a **Device**) and several others sub-**Modules** containing the **Variables** and **Actions** of each associated modules.

.. code-block:: python

	-- XPS Controller (Module/Device)
		|-- ND Filter (Module)
			|-- Angle (Variable)
			|-- Transmission (Variable)
			|-- Homing (Action)
		|-- Linear stage (Module)
			|-- Position (Variable)
			|-- Homing (Action)		
			
This hierarchy is implemented for each instrument in its drivers files.

Open a Device
-----------------------

To use this interface, you need to store locally the configuration of your intruments (see :re:`configuration`).

For a given instrument, the associated hierarchy of **Elements** is implemented in the drivers files, and is thus ready to use.
Each **Elements** is represented by a name. The name of the top-level **Module**, the **Device**, is the nickname of the instrument in the configuration file (see :re:`configuration`).

To see the list of the available **Devices**, simply use the function ``list_devices`` of Autolab. 

.. code-block:: python

	>>> import autolab
	>>> autolab.list_devices()
	['my_tunics','my_power_meter','my_linear_stage']

.. note::

The function ``show_devices`` displays the list of the available **Devices**, with an indication of their loaded status.

.. code-block:: python

	>>> autolab.show_devices()

To open a **Device**, simply call the function ``get_device`` with the name of the **Device**.

.. code-block:: python

	>>> lightSource = autolab.get_device('my_tunics')
	
To close a **Device**, simply call its the function ``close``. This object will not be usable anymore.

.. code-block:: python

	>>> lightSource.close()
	
Navigation in a Device
--------------------

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
	
Let's see now how to use concretely these **Elements**.

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
	
	# Open the Devices
	myTunics = autolab.get_device('my_tunics')
	myPowerMeter = autolab.get_device('my_power_meter')
	
	# Turn on the light source
	myTunics.output(True)
	
	# Sweep its wavelength and measure a power with a power meter
	wl_list = []
	power_list = []
	for wl in range(1550,1560,0.01) :
	
	    # Set the parameter
	    myTunics.wavelength(wl)
	    
	    # Measures the values
	    wl_measured = myTunics.wavelength(wl)
	    power = myPowerMeter.line1.power()
	    
	    # Store the values in a list
	    wl_list.append(wl_measured)
	    power_list.append(power)
	
	# Turn off the light source
	myTunics.output(False)



