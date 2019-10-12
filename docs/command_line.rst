.. _commandline:

Command-line operation
======================

To start using Autolab, open a Python shell and import the package:

.. code-block:: python

	>>> import autolab

To see which devices are currently configured locally on your system, call the function ``help`` of the object ``autolab.devices``:

.. code-block:: python

	>>> autolab.devices.help()

To configure a new device on your system, see the section :ref:`configuration`.

To establish a connection to a given device, just call the corresponding attribute name in ``autolab.devices``:

.. code-block:: python

	>>> autolab.devices.myTunics
	
You can close an existing connection to the instrument by calling the function ``close`` of the device:

.. code-block:: python

	>>> autolab.devices.myTunics.close()
	
You can reload (close and reconnect) the connection to the instrument by calling the function ``reload`` of the device:

.. code-block:: python

	>>> autolab.devices.myTunics.reload()
	
You can close all existing connections (with all instruments) by calling the function ``close_all`` of the object ``autolab.devices``:

.. code-block:: python

	>>> autolab.devices.close_all()

Device architecture
-------------------

As explained in the section :ref:`introduction`, a device is represented in Autolab by a hierarchy of three **Elements**: the **Modules**, the **Variables** and the **Actions**.

You can retrieve this hierarchy in the object ``autolab.devices``, where you can navigate between these **Elements** directly with relative attributes. For instance, to access the **Variable** ``wavelength`` of the **Module** (**Device**) ``myTunics``, simply execute the following command:

.. code-block:: python

	>>> autolab.devices.myTunics.wavelength
	
In the case of a more complex module, for instance a power meter named ``myPowerMeter`` with different lines, you can access the **Variable** ``power`` of the first line ``line1`` with the following command:

.. code-block:: python

	>>> autolab.devices.myPowerMeter.line1.power
	
Every **Element** has a function ``help`` that can be called to obtain some information about it. For a **Module**, it will display the list of its **Variables**, **Actions** and sub-**Modules**. For a **Variable**, it will display its read and/or write functions (from the driver) and its unit if provided in the driver. For a **Action**, il will display the associated function in the driver.

.. code-block:: python

	>>> autolab.devices.myTunics.help()
	>>> autolab.devices.myTunics.wavelength.help()
	>>> autolab.devices.myPowerMeter.line1.power.help()
	
	

Variables
---------

If a **Variable** is readable (read function provided in the driver), its current value can be read by calling its attribute:

.. code-block:: python

	>>> autolab.devices.myTunics.wavelength()
	1550.55
	>>> autolab.devices.myTunics.output()
	False

If a **Variable** is writable (write function provided in the driver), its current value can be set by calling its attribute with the desired value:

.. code-block:: python

	>>> autolab.devices.myTunics.wavelength(1549)
	>>> autolab.devices.myTunics.output(True)
	

Actions
-------

You can execute an **Action** by calling its attribute:

.. code-block:: python

	>>> autolab.devices.myLinearStage.goHome()
	
	
Script example
--------------

With all these commands, you can now create your own Python script. Here is an example of script that sweep the wavelength of a light source, and measure the power of a power meter:

.. code-block:: python

	import autolab
	
	myTunics = autolab.devices.myTunics
	myPowerMeter = autolab.devices.myPowerMeter
	
	# Turn on the light source
	myTunics.output(True)
	
	# Sweep its wavelength and measure a power with a power meter
	wl_list = []
	power_list = []
	for wl in range(1550,1560,0.01) :
	    myTunics.wavelength(wl)
	    power = myPowerMeter.line1.power()
	    wl_list.append(wl)
	    power_list.append(power)
	
	# Turn off the light source
	myTunics.output(False)


Help and bugs/suggestions report
--------------------------------

In case you need some help to use Autolab, you can open directly this documentation in your web browser by calling the function ``help`` of the package:

.. code-block:: python

	>>> autolab.help()

	
If you encounter some problems or bugs, or if you have any suggestion to improve this package, or one of its driver, please open an Issue on the GitHub page of this project: 
https://github.com/qcha41/autolab/issues/new

You can also directly call the function ``report`` of the package, which will open this page on your web browser:

.. code-block:: python

	>>> autolab.report()
