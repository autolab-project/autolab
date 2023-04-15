.. _create_driver:

Write your own Driver
=====================

The goal of this tutorial is to present the general structure of the drivers of this package, in order for you to create simply your own drivers, and make them available to the community within this collaborative project. We notably provide a fairly understandable driver structure that can handle the highest degree of instruments complexity (including: single and multi-channels function generators, oscilloscopes, Electrical/Optical frames with associated interchangeable submodules, etc.). This provides reliable ways to add other types of connection to your driver (e.g. GPIB to Ethenet) or other functions (e.g. get_amplitude, set_frequency, etc.).

.. note::

    To help you with writting your own drivers a few templates are provided on the `GitHub page of the project <https://github.com/qcha41/autolab/tree/master/autolab/drivers/More/Templates>`_.

We will first discuss the generalities to create a new driver or modify an existing one and share it with the community in **getting started: create a new driver**, that will particularly describe the required convention (location, files and namings) as well as the actual way to share it with the community (addition to the main package), and finally we will detail the typical **driver structure** as well as the required homogeneities. Those last will ensure that all the features of the drivers you would add are best used by autolab's utilities (helps, gui, parser, etc.).


Getting started: create a new driver
------------------------------------

**To develop your own drivers**, autolab provide you with a directory named local_drivers (located at ~/autolab/local_drivers, where ~ represents the user root) created when the package is installed. This directory is inspected by autolab to search for locally defined drivers. This way you may modify existing drivers (addition of new functions, etc.) or create new drivers to drive new instruments not yet supported by autolab.

.. note::

    Each driver name should be unique: do not define new drivers (in your local folders) with a name that already exists in the main package.


In the local_drivers directory, as in the main package, each instrument has/should have its own directory organized and named as follow. The name of this folder take the form *\<manufacturer\>_\<MODEL\>*. The driver associated to this instrument is a python script taking the same name as the folder: *\<manufacturer\>_\<MODEL\>.py*. A second python script, allowing the parser to work properly, should be named *\<manufacturer\>_\<MODEL\>_utilities.py* (`find a minimal template here <https://github.com/qcha41/autolab/tree/master/autolab/drivers/More/Templates>`_). Additional python scripts may be present in this folder (devices's modules, etc.). Please see the existing drivers of the autolab package for extensive examples.

**For addition to the main package**: Once you tested your driver and it is ready to be used by others, you can send the appropriate directory to the contacts (:ref:`about`).


.. warning::

    **General note**

    * The imports of additional modules (numpy, pandas, time, etc.) should be made in the class they are needed so that the imports are done only if needed (e.g. import visa within the Driver_VISA class).

Driver structure (*\<manufacturer\>_\<MODEL\>.py* file)
-------------------------------------------------------

The Driver is organized in several `python class <https://docs.python.org/tutorial/classes.html>`_ with a structure as follow. The numbers represent the way sections appear from the top to the bottom of an actual driver file. We chose to present the sections in a different way:

1 -  import modules (optionnal)
###############################

    To import possible additional modules, e.g.:

    .. code-block:: python

        import time
        from numpy import zeros,ones,linspace

3 -  class Driver_CONNECTION
############################

    The class Driver_CONNECTION: **establish the connection with the instrument** and **define the communication functions**.

    As a reminder, a communication with an instruments occurs in general with strings that are set by the manufacturer and instrument and model dependent. To receive and send strings from and to the instrument we first need to establish a connection. This will be done using dedicated python package such as `pyvisa`, `pyserial`, `socket` and physical connections such as Ethernet, GPIB, or USB. See bellow for an example help with using a VISA type of connection.

    .. caution::
        The connection types are refered to with capital characters in the classes names, e.g.:

        .. code-block:: python

            class Driver_SOCKET():
            class Driver_TELNET():


    When using the driver module (.py) the Driver_CONNECTION class is imported as the top layer, it inherits all the attributes of the Driver class and run its ``__init__`` function. It is the class that is used. Note that the connection classes are located, within a driver module, bellow the Driver class, because they use it before reaching their own ``__init__`` function.

    Here is a commented example of the Driver_CONNECTION class, further explained bellow:

    .. code-block:: python

        #################################################################################
        ############################## Connections classes ##############################
        class Driver_VISA(Driver):           # Inherits all the attributes of the class Driver
            def __init__(self, address='GPIB0::2::INSTR',**kwargs):  # 0) Definition of the ``__init__`` function
                import pyvisa as visa                 # 1) Connection library to use

                rm = visa.ResourceManager()  # Use of visa's ressource manager
                self.inst = rm.get_instrument(address) # 2) Establish the communication with the instrument

                Driver.__init__(self)        # 3) Run what is define in the Driver.__init__ function

            # Communication functions
            def write(self,command):         # 4) Defines a write function
                self.inst.write(command)     # Sends a string 'command' to the instrument
            def read(self):                  # 5) Defines a read function
                rep = self.inst.read()       # Receives a string 'rep' from the instrument and return it
                return rep
            def query(self,query):           # 6) Defines a query function: combine your own write and read functions to send a string and ask for an answer
                self.write(query)
                return self.read()
            def close(self):                 # 7) Closes the communication
                self.inst.close()
        ############################## Connections classes ##############################
        #################################################################################


    In this case the Driver_CONNECTION class is called ``Driver_VISA``. To use a driver we usually create an instance of the Driver_CONNECTION class (cf. :ref:`userguide_low`):

    .. code-block:: python

        >>> Instance = Driver_VISA(address='GPIB0::3::INSTR')   # Use the given `visa` address (i.e., GPIB address 3 and board_index 0)

    This execute the ``__init__`` function that (following this example labels):
        1\) import the connection type library

        2\) load the instrument (using its address and eventual other arguments)

        3\) run the Driver.__init__ (for everything not related with the connection to the instrument, detailed in the Driver class section)

    In general, the ``__init__`` function should establish the connection and store the instrument Instance in a class attribute (here: ``self.inst``). (The communication functions that follow will use this attribute.)

    Importantly, the communication functions are (re-)defined in this class including write [4)], read [5)], query [6)] and close [7)] functions that are the bare minimum. They are the ones that must be used in all the other classes (Driver, Module\_, etc.). They must take **a string as argument** and **return a string**, **without any termination character** (e.g. ``\n``, ``\r``, etc.). This way several connection classes can coexist and use the same other classes allowing different possible physical connections and in general more flexibility.

    .. caution::

        Several points are worth noting:

            - 0\) The ``__init__`` function definition should explicitely contain all the arguments that are necessary to establish the communication (in this exemple ``address``) along with a default value (for example the one that works for you), in order for the automatic autolab help to behave properly. The ``__init__`` function definition should also have an extra argument ``**kwargs`` allowing to accept and possibly pass any extra argument provided.

            - 3\) For more complicated instruments an additional argument ``**kwargs`` would be provided, giving:

                .. code-block:: python

                    Driver.__init__(self,**kwargs)

                This enables passing extra arguments (e.g. slot configuration, etc.) to the Driver class, that will instantiate the instrument configuration, in the form of a dictionnary.

            - 7\) The close function is mandatory, even though you do not use it in any of the other classes of the  *\<manufacturer\>_\<MODEL\>.py* file.


    **Further instrument complexity:**

        With further instrument and/or connection type complexity you will need to add other arguments to the ``__init__`` function of Driver_CONNECTION class. As an example to add an argument board_index for a GPIB connection type, you would need to modify the example line 0\) to:

        .. code-block:: python

            def __init__(self, address=19,board_index=0,**kwargs):

        You may also need to pass arguments to the class Driver (see next section), that may come from e.g. the number of channels of an oscilloscope or the consideration of an instrument with *slots*, you would need to modify line 3\) of the example:

        .. code-block:: python

            Driver.__init__(self,**kwargs)


        Please check out autolab existing drivers for more examples and/or to re-use existing connection classes (those would most likely need small adjustments to fit your instruments).


    .. note:: **Help for VISA addresses**

        For `visa` module to work properly, you need to provide an address for communication, that you may be able to get types the few next lines:

        .. code-block:: python

            import pyvisa as visa
            rm = visa.ResourceManager()
            rm.list_resources()

        Just execute them before and after plugging in your instrument to see which address appears. For ethernet connections, you should know the IP address (set it to be part of your local network) and the port (instrument documentation) of your instrument.

        Examples of visa addresses may be `find here online <https://pyvisa.readthedocs.io/en/latest/>`_ :

        .. code-block:: python

            TCPIP::192.168.0.5::INSTR
            GPIB0::3::INSTR



2 -  class Driver
#################

    The class Driver: **establish the connection with internal modules or channels** (optionnal as dependant on the instrument, see next section) and **define instrument-related functions**.

    After the communication with your instrument is established, we need to send commands or receive answers (to get the results of a query or a requested command). The communication part being manage by the class Driver_CONNECTION, any time we want to send a (instrument-specific) command to the instrument from the class Driver, we need to use the communication functions defined in the class Driver_CONNECTION.

    The class Driver_CONNECTION inherits all the attributes of the class Driver. The function ``__init__`` of the class Driver is run by the class Driver_CONNECTION. The Driver class will act as your main instrument.

    Here is a commented example of the class Driver, further explained bellow:

    .. code-block:: python

        class Driver():
            def __init__(self):                    # 1) Definition of the ``__init__`` function
                import time                        # 2) Additional imports and/or setup additional attributes

                self.write('VUNIT MV')             # 3) Run additional commands to instantiate the instrument (e.g. set the vertical unit to be used)

            def set_amplitude(self,amplitude):     # 4) Defines a function to set a value to the instrument
                self.write(f'VOLT {amplitude}')    # 5) Sets the amplitude, instrument specific
            def get_amplitude(self):               # 6) Defines a function to query a value to the instrument
                return float(self.query(f'VOLT?')) # 7) Returns the amplitude, instrument specific
            def single_burst(self):                # 8) Defines a function to perform an action
                self.write('BRST SINGLE')          # 9) Triggers a single burst, instrument specific

            def idn(self):                         # 10) This function should work with all instruments
                self.write('*IDN?')                # 11) '*IDN?' should be understood by all instruments
                return self.read()                 # 12) Returns the identification of an instrument


    When the class Driver_CONNECTION is is instantiated, the ``__init__`` function is executed. It does the following (following this example labels):
        1\) import additional libraries

        2\) run additional commands to instantiate the instrument (e.g. set the vertical unit to be used)

    .. caution::

        For further instrument complexity, including multi-channels instruments (generators, oscilloscopes, etc.) or instruments with `slots`, the instantiation of additional classes must be done here. See the following examples.

    In general, the ``__init__`` function should run instrument-related initializations. If nothing in particular needs to be done then, one can just:

    .. code-block:: python

        def __init__(self,nb_channels=2):       # 1)
            pass

    Importantly, the class Driver defines all the functions that are related to the main instrument: to set [4)]/query [6)] some values (e.g. the output amplitude of a function generator) or perform actions (e.g. trigger a single burst event).

    .. caution::

        Several points are worth noting:

            1) Favor python f strings (``f''``) that are more, especially when an argument has to be passed to the function, that are more robust to different types [5)].

            2) You should explicitely convert the string returned by Driver_CONNEXION.query() (or Driver_CONNEXION.read) to the expected `variable` type [7)].

            3) For more complex instruments (i.e. with additional classes), please refer to the next section. In general, only the functions associated with the **main** instrument should be found here.


    **Further instrument complexity:**

        Here is a way to modify the ``__init__`` function of the class Driver to deal with the case of a **multi-channel instrument**. (Note: some of the lines have been removed from the previous example for clarity.) It is further explained bellow:

        .. code-block:: python

            def __init__(self,nb_channels=2):       # 1) Definition of the ``__init__`` function

                self.nb_channels = int(nb_channels) # 2) Set arguments given to the class as class attributes to be re-used elsewhere (within the class)

                for i in range(1,self.nb_channels+1):
                    setattr(self,f'channel{i}',Channel(self,i)) # 3) Set additional Module\_MODEL classes (called Channel here) as classes attibutes

        Here, the number of channels is provided as argument to the ``__init__`` function [1)], and for each channel [3)] an attribute of the class Driver is created by instantiating an additional class called **Channel**. The line 3) is formally equivalent to (considering: i=1):

        .. code-block:: python

            self.channel1 = Channel(self,1)

        All the channels are thus equivalent in this example as they use the same additional class (**Channel**). The arguments provided to the class **Channel** are: all the attributes of the actual class (**Driver**) and the number of the instantiated channel; both will be used in the additional class (e.g. the connection functions, etc.)

        The previous structure should be used only if the physical slot configuration is naturally fixed by the manufacturer (a power meter with two channels for instance). In the particular case of an **instrument with `slots`**, all the `channels` are not equivalent. They rely on different physical modules that may be disposed differently and in different numbers for different users. Then one class for each different module (that are inserted in a main frame) should be defined (**Module_MODEL**).
        Here is a way to modify the ``__init__`` function of the class Driver to deal with the case of an instrument with `slots`:

        .. code-block:: python

            def __init__(self, **kwargs):

                ### Submodules loading
                self.slot_names = {}
                prefix = 'slot'
                for key in kwargs.keys():
                    if key.startswith(prefix) and not '_name' in key :
                        slot_num = key[len(prefix):]
                        module_name = kwargs[key].strip()
                        module_class = globals()[f'Module_{module_name}']
                        if f'{key}_name' in kwargs.keys() : name = kwargs[f'{key}_name']
                        else : name = f'{key}_{module_name}'
                        setattr(self,name,module_class(self,slot_num))
                        self.slot_names[slot_num] = name

        This will parse the arguments received by the ``__init__`` function (of the class **Driver**) in the ``**kwargs`` appropriately to instantiate the right combination Modules/Slots providing the Modules (additional classes) follow some naming conventions (explained in the next section).

        .. note::

            For the particular case of instruments that one usually gets 1 dimensionnal traces from (e.g. oscilloscope, spectrum annalyser, etc.), it is useful to add to the class Driver some user utilities such as procedure for channel acquisitions:

            .. code-block:: python

                ### User utilities
                def get_data_channels(self,channels=[],single=False):
                    """Get all channels or the ones specified"""
                    previous_trigger_state = self.get_previous_trigger_state()                   # 1)
                    self.stop()                                                                  # 2)
                    if single: self.single()                                                     # 3)
                    while not self.is_stopped(): time.sleep(0.05)                                # 4)
                    if channels == []: channels = list(range(1,self.nb_channels+1))
                    for i in channels:
                        if not(getattr(self,f'channel{i}').is_active()): continue
                        getattr(self,f'channel{i}').get_data_raw()                               # 5)
                        getattr(self,f'channel{i}').get_log_data()                               # 6)
                    self.set_previous_trigger_state(previous_trigger_state)                      # 7)

                def save_data_channels(self,filename,channels=[],FORCE=False):
                    if channels == []: channels = list(range(1,self.nb_channels+1))
                    for i in channels:
                        getattr(self,f'channel{i}').save_data_raw(filename=filename,FORCE=FORCE) # 8)
                        getattr(self,f'channel{i}').save_log_data(filename=filename,FORCE=FORCE) # 9)

            These functions rely on some other functions that should be implemented by the user (``single``, ``get_previous_trigger_state``, etc.). The reader may find a `find a full template example here <https://github.com/qcha41/autolab/tree/master/autolab/drivers/More/Templates>`_.

            Overall, the function get_data_channels:
                1) Store the previous trigger state
                2) Stop the instrument
                3) Trigger a single trigger event (if requested)
                4) Wait for the scope to be stopped
                5) Acquire the channels provided (all if no channel is provided)
                6) Acquire the logs of the channels provided (all if no channel is provided)
                7) Set the previous trigger state back

            Overall, the function save_data_channels:
                8) Save the channels provided (all if no channel is provided)
                9) Save the logs of the channels provided (all if no channel is provided)

.. _additional_class:

4 -  Additional class (optionnal)
#################################

    .. Caution::

        **Additional classes namings**

        The additional classes should be named **Module\_MODEL**. Exceptions do occur for some oscilloscopes (**Channel**), spectrum annalyser (**Trace**) or some multi-channel instruments (**Output**), in which case we stick to the way it is refered to as in the Programmer Manual of the associated instrument.

    In the particular case of an **instrument with `slots`**, all the `channels` are not equivalent. They rely on different physical modules that may be disposed differently and in different numbers for different users. Then one class for each different module (that are inserted in a main frame) should be defined (**Module_MODEL**). The ``__init__`` function of the class **Driver** will deal with which class **Module_MODEL** to instantiate with which `slot` depending on the actual configuration of the user.
    Thus the class **Module_MODEL** (or **Channel**, etc.) have all a similar structure, structure that is similar to the one of the class Driver. In other words the class **Driver** deal with the `main` instruments while the additional classes deal with the sub-modules.

    Here is an example of the class Channel of a double channel function generator:

    .. code-block:: python

        class Channel():
            def __init__(self,dev,channel):
                self.channel = int(channel)
                self.dev     = dev

            def amplitude(self,amplitude):
                self.dev.write(f':VOLT{self.channel} {amplitude}')
            def offset(self,offset):
                self.dev.write(f':VOLT{self.channel}:OFFS {offset}')
            def frequency(self,frequency):
                self.dev.write(f':FREQ{self.channel} {frequency}')

    Here is an example of the two class Module_MODEL of a instrument with `slot` for which slots are non-equivalent (strings needed to perform the same actions are different):

    .. code-block:: python

        class Module_TEST111() :
            def __init__(self,driver,slot):
                self.driver = driver
                self.slot   = slot

            def set_power(self,value):
                self.dev.write(f'POWER={value}')
            def get_power(self):
                return float(self.dev.query('POWER?'))

        class Module_TEST222() :
            def __init__(self,driver,slot):
                self.driver = driver
                self.slot   = slot

            def set_power(self,value):
                self.dev.write(f'POWER={value}')
            def get_power(self):
                return float(self.dev.query('POWER?'))

    One can note (for both cases):

        1) In the ``__init__`` function both the driver ``self`` and the channel/slot naming are passed to an attribute of the actual class (**Channel**, **Module_TEST111**, **Module_TEST222**).

        2) The connection functions used are the one coming from the class **Driver**, thus one now call them ``self.dev.connection_function`` (for connection_function defined in the class **Driver_CONNECTION** in: write, read, query, etc.).

        3) Finally there is a collection of functions that are `channel`/`slot`-dependant.

    .. note::

        For the particular case of instruments that one usually gets 1 dimensionnal traces from (e.g. oscilloscope, spectrum annalyser, etc.), it is useful to define functions to get and save the data. See the folliwing instrument dependant example:

        .. code-block:: python

            def get_data_raw(self):
                if self.autoscale:
                    self.do_autoscale()
                self.dev.write(f'C{self.channel}:WF? DAT1')
                self.data_raw = self.dev.read_raw()
                self.data_raw = self.data_raw[self.data_raw.find(b'#')+11:-1]
                return self.data_raw
            def get_data(self):
                return frombuffer(self.get_data_raw(),int8)
            def get_log_data(self):
                self.log_data = self.dev.query(f"C{self.channel}:INSP? 'WAVEDESC'")
                return self.log_data

            def save_data_raw(self,filename,FORCE=False):
                temp_filename = f'{filename}_WAVEMASTERCH{self.channel}'
                if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
                    print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
                    return
                f = open(temp_filename,'wb')# Save data
                f.write(self.data_raw)
                f.close()
            def save_log_data(self,filename,FORCE=False):
                temp_filename = f'{filename}_WAVEMASTERCH{self.channel}.log'
                if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
                    print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
                    return
                f = open(temp_filename,'w')
                f.write(self.log_data)
                f.close()

        Those will then be attributes of the class **Channel** and may be called from the class **Driver** (depending on the channel's instance name in this class):

        .. code-block:: python

            self.channel1.get_data()


Additional necessary functions/files
------------------------------------

.. _get_driver_model:

Function get_driver_model (in each class but Driver_CONNECTION)
###############################################################

The function ``get_driver_model`` should be present in each of the classes of the *\<manufacturer\>_\<MODEL\>.py* but the class **Driver_CONNECTION** (including the class Driver and any optionnal class **Module_MODEL**), in order for many features of the package to work properly. It simply consists in a list of predefined elements that will indicate to the package the structure of the driver and predefined variable and actions.
There are three possible elements in the function ``get_driver_model``: *Module*, *Variable* and *Action*.

Shared by the three elements (*Module*, *Variable*, *Action*):
    - 'name': nickname for your element (argument type: string)
    - 'element': element type, exclusively in: 'module', 'variable', 'action' (argument type: string)
    - 'help': quick help, optionnal (argument type: string)
*Module*:
    - 'object' : attribute of the class (argument type: Instance)
*Variable*:
    - 'read': class attribute (argument type: function)
    - 'write': class attribute (argument type: function)
    - 'type': python type, exclusively in: int, float, bool, str, bytes, np.ndarray, pd.DataFrame
    - 'unit': unit of the variable, optionnal (argument type: string)

    .. caution::
        Either 'read' or 'write' key, or both of them, must be provided.

*Action*:
    - 'do' : class attribute

Example code:

.. code-block:: python

    def get_driver_model(self):
        model = []
        model .append({'name':'line1', 'element':'module','object':self.slot1,'help':'Simple help for line1 module'})
        model .append({'name':'amplitude', 'element':'variable', 'type':float, 'read':self.get_amplitude, 'write':self.set_amplitude, 'unit':'V', 'help':'Simple help for amplitude variable'}
        model.append({'name':'go_home', 'element':'action', 'read':self.home, 'help':'Simple help for go_home action'})
    return model

.. _name_driver_utilities.py:

Driver utilities structure (*\<manufacturer\>_\<MODEL\>_utilities.py* file)
###########################################################################

This file should be present in the driver directory (*\<manufacturer\>_\<MODEL\>.py*).

Here is a commented example of the file *\<manufacturer\>_\<MODEL\>_utilities.py*, further explained bellow:

.. code-block:: python

    category = 'Optical source'                                #

    class Driver_parser():                                     #
        def __init__(self, Instance, name, **kwargs):          #
            self.name     = name                               #
            self.Instance = Instance                           #


        def add_parser_usage(self,message):                    #
            """Usage to be used by the parser"""               #
            usage = f"""                                       #
    {message}                                                  #
                                                               #
    ----------------  Examples:  ----------------              #
                                                               #
    usage:    autolab driver [options] args                    #
                                                               #
        autolab driver -D {self.name} -A GPIB0::2::INSTR -C VISA -a 0.2
        load {self.name} driver using VISA communication protocol with address GPIB... and set the laser pump current to 200mA.
                """                                            #
            return usage                                       #

        def add_parser_arguments(self,parser):                 #
            """Add arguments to the parser passed as input"""  #
            parser.add_argument("-a", "--amplitude", type=str, dest="amplitude", default=None, help="Set the pump current value in Ampere." )

            return parser                                      #

        def do_something(self,args):                           #
            if args.amplitude:                                 #
                # next line equivalent to: self.Instance.amplitude = args.amplitude
                getattr(self.Instance,'amplitude')(args.amplitude)

        def exit(self):                                        #
            self.Instance.close()                              #


It contains:

    * The category of the instrument (see ``autolab.infos`` (from python shell) or ``autolab infos`` for (OS shell) for examples of identified categories).

    * A class **Driver_parser** with 5 functions:

        **1**) ``__init__``: defines class attributes

        **2**) ``add_parser_usage``: adds help to the parser in order to help the user

        **3**) ``add_parser_arguments``: configures options to be used from the OS shell (e.g. ``autolab driver -D nickname -a 2``). See :ref:`os_driver` for full usage.

        **4**) ``do_something``: configures action to perform/variable to set (here: modify the amplitude to the the provided argument value), and link them to the values of the argument added with **3**).

        **5**) ``exit``: closes properly the connection

.. note::

    Please do consider, keeping each line ending with a # character in the example as is.This way you would need to modify 3 main parts to configure options, associated actions and help:  **3**), **4**) and **2**) (respectively).
