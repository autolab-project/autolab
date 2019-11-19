.. _shell_connection:

The two sections that follow are equivalent for the commands ``autolab driver`` and ``autolab device`` (unless specified). They will guide you through **getting basic help** and minimal formatting of command lines (minimal arguments to pass) to **establish the connection with you instrument**.

.. _name_shell_help:

Getting help
============

Three helps are configured (device or driver may be used equally in the lines bellow):
    
    1) Basic help of the commands autolab driver/device: 
    
        .. code-block:: python
        
            >>> autolab driver -h
            
        It including arguments and options formatting, definition of the available options and associated help and informations to retrieve the list of available drivers and local configurations (command: autolab infos).
    
    2) Basic help about the particular name driver/device you provided:
    
        .. code-block:: python
        
            >>> autolab driver -h -D driver_name
    
        It includes the category of the driver/device (e.g. Function generator, Oscilloscope, etc.), a list of the implemented connections (-C option), personnalized usage example (automatically generated from the driver.py file), and examples to use and set up a local configuration using command lines (see :ref:`localconfig` for more informations about local configurations).
    
    3) Full help message **about the driver/driver**:
    
        .. code-block:: python
        
            >>> autolab driver -D driver_name -C connection -A address -h
            >>> autolab driver -D nickname -h
    
        **For driver:** 
            
            It includes the list of the implemented connections (-C option), the list of the available additional modules (classes **Channel**, **Trace**, **Module_MODEL**, etc.; see :ref:`create_driver`), the list of all the methods that are instantiated with the driver (for direct use with the command: autolab driver; see :ref:`os_driver`), and an extensive help for the usage of the defined options.
            
        **For device:**
            
            It includes the hierarchy of the device and all the defined *Modules*, *Variables* and *Actions* (see :ref:`get_driver_model` and :ref:`os_device` for more informations on the definition and usage respectively).
            
        Note that this help requires the instantiation of your instrument to be done, in other words it requires valid arguments for options -D, -C and -A (that you can get for previous helps) and a working physical link.

.. _name_shell_connection:

Connection arguments
====================

The commands autolab driver/device will establish a connection to your instrument, perform the requested operation, and finally close properly the connection. To **establish the connection** you need to give valid arguments as requested by the driver (build to suit the physical instrument requirements). 

.. code-block:: python

    >>> autolab driver -D <driver_name or config_name> -C <CONNECTION> -A <address> (optional)


To establish the connection for the first time, we recommand to follow the different help states (see :ref:`_name_shell_help`).
    

-P --port Argument used to address different things depending on the connection type. SOCKET: the port number used to communicate, GPIB: the gpib board index, DLL: the path to the dll library.
-O --other Set other parameters (slots,...).

    


    
    
    
