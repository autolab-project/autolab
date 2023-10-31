.. _shell_connection:

The two sections that follow are equivalent for the commands ``autolab driver`` and ``autolab device`` (unless specified). They will guide you through **getting basic help** and minimal formatting of command lines (minimal arguments to pass) to **instantiate your instrument** (set up the connection with it, etc.).

.. _name_shell_help:

Getting help
============

Three helps are configured (device or driver may be used equally in the lines bellow):

    1) Basic help of the commands autolab driver/device:

        .. code-block:: none

            >>> autolab driver -h

        It including arguments and options formatting, definition of the available options and associated help and informations to retrieve the list of available drivers and local configurations (command: autolab infos).

    2) Basic help about the particular name driver/device you provided:

        .. code-block:: none

            >>> autolab driver -h -D driver_name

        It includes the category of the driver/device (e.g. Function generator, Oscilloscope, etc.), a list of the implemented connections (-C option), personnalized usage example (automatically generated from the driver.py file), and examples to use and set up a local configuration using command lines (see :ref:`localconfig` for more informations about local configurations).

    3) Full help message **about the driver/device**:

        .. code-block:: none

            >>> autolab driver -D driver_name -C connection -A address -h
            >>> autolab device -D nickname -h

        **For driver:**

            It includes the list of the implemented connections (-C option), the list of the available additional modules (classes **Channel**, **Trace**, **Module_MODEL**, etc.; see :ref:`create_driver`), the list of all the methods that are instantiated with the driver (for direct use with the command: autolab driver; see :ref:`os_driver`), and an extensive help for the usage of the pre-defined options.

        **For device:**

            It includes the hierarchy of the device and all the defined *Modules*, *Variables* and *Actions* (see :ref:`get_driver_model` and :ref:`os_device` for more informations on the definition and usage respectively).

        Note that this help requires the instantiation of your instrument to be done, in other words it requires valid arguments for options -D, -C and -A (that you can get for previous helps) and a working physical link.

.. _name_shell_connection:

Instantiate a driver/device
===========================

The commands autolab driver/device will set up a connection to your instrument, perform the requested operation(s), and finally close properly the connection. To **set up the connection** you need to give valid arguments as requested by the driver (build to suit the physical instrument requirements).

A typical command line structure is:

.. code-block:: none

    >>> autolab driver -D <driver_name> -C <CONNECTION> -A <address> (optional)
    >>> autolab device -D <config_name> (optional)

**To set up the connection** for the first time, we recommand to follow the different help states (see :ref:`name_shell_help`), that usually guide you through filling the arguments corresponding to the above options. To use one of Autolab's driver to drive an instrument you need to provide its name. This is done with the option -D. -D option accepts a driver_name for a driver (e.g. agilent_33220A, etc) and a config_name for a device (nickname as defined in your device_config.ini, e.g. my_agilent). A full list of the available driver names and config names may be found using the command ``autolab infos``. Due to Autolab's drivers structure you also need to provide a -C option for the connection type (corresponding to a class to use for the communication, see :ref:`create_driver` for more informations) when instantiating your device. The available connection types (arguments for -C option) are driver dependent (you need to provide a valid -D option) and may be access with a second stage help (see :ref:`name_shell_help`).
Lately you will need to provide additional options/arguments to set up the communication. One of the most common is the address for which we cannot help much. At this stage you need to make sure of the instrument address/set the address (on the physical instrument) and format it the way that the connection type is expecting it (e.g. for an ethernet connection with address 192.168.0.1 using VISA connection type: ``TCPIP::192.168.0.1::INSTR``). You will find in the second stage help automatically generated example of a minimal command line (as defined in the driver) that should be able to instantiate your instrument (providing you modify arguments to fit your conditions).

**Other arguments** may be necessary for the driver to work properly. In particular, additional connection argument may be passed through the option -O, such as the port number (for SOCKET connection type), the gpib board index (for GPIB connection) or the path to the dll library (for DLL connection type).
In addition, for `complex` instruments (such as instruments with 'slots'), this options provides you with a reliable way to indicate the physical configuration of your instrument [e.g. Module_TEST111 is physically inserted in slot 1, Module_TEST222 is physically inserted in slot 5 (-O slot1=Module_TEST111 slot5=Module_TEST222); see :ref:`additional_class` for more informations].
