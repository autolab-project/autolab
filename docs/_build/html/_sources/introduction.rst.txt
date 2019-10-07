Introduction
============

Autolab provides a set of drivers to communicate with several laboratory instruments. In this Python package, a physical instrument is fully described with a hierarchy of three particular entities: the **Modules**, the **Variables** and the **Actions**.

	* A **Module** is a group of **Variables**, **Actions**, and sub-**Modules**. 
	* A **Variable** refers to a physical quantity, whose the value can be either set and/or read from an instrument (wavelength of an optical source, position of a linear stage, optical power measured with a power meter, spectrum measured with a spectrometer...). Depending on the nature of the physical quantity, it can optionally have a unit.
	* An **Action** refers to a particular operation that can be performed by an instrument. (homing of a linear stage, the zeroing of a power meter, the acquisition of a spectrum with a spectrometer...)

.. note::

	A **Device** is the top level **Module** of an instrument.
	
A simple instrument is usually composed of only one **Module**, and a few **Variables** and **Actions** attached to it.

.. code-block::

	-- Tunics (Module/Device)
		|-- Wavelength (Variable)
		|-- Output state (Variable)
	

Some instruments can host several differents modules. Their representation in Autolab generally consists in one top level **Module** (the frame) and several others sub-**Modules** containing the **Variables** and **Actions** of each associated modules.

.. code-block::

	-- XPS Controller (Module/Device)
		|-- ND Filter (Module)
			|-- Angle (Variable)
			|-- Transmission (Variable)
			|-- Homing (Action)
		|-- Linear stage (Module)
			|-- Position (Variable)
			|-- Homing (Action)		
			
We will see in the sections :ref:`commandline` and :ref:`gui` how this modelization is useful to provide a user-friendly and straightforward remote control of your instrument.

First of all, let's install the package on your computer.
