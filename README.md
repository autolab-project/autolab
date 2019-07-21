# USIT : Universal Scanning Interface 

__Python package for scientific experiments automation__

Created by Quentin Chateiller, PhD student at C2N (Center for Nanosciences and Nanotechnologies, Palaiseau, France) in the ToniQ (Sandwich) group.

The purpose of this package it to provide easy and efficient tools to deal with your scientific instruments, and to run automated experiments with them. 

Package development ongoing, some features are still not present yet.

## Quick start
___

After installing this package, import it in a python console. To work properly, USIT need to store configuration files in your computer. A local folder *usit* will be created in your home directory the first time you import USIT (or if you deleted it), and place a configuration file inside :

```python
import usit
# It will output the fist time:
# USIT local folder created : <your_user_path>
# Local config.ini file not found, duplicated from package in the local folder.
```

At the first time, you may also have an additional message saying that your *config.ini* file is not well configured. Indeed, in order to access your devices with USIT, you need to indicate to the package some informations about the location of your drivers and your local device configuration. To do that, you need to update the config.ini that has been created in your home directory (see instructions below). Once this is done, you can continue.

To see what are the available devices, just access the `devices` attribute of `usit`:
```python
usit.devices           # or
print(usit.devices.get_available_devices())
```
This list corresponds to the devices list have configured in an *Device Index* configuration file (see after). To access one particular device, just access the corresponding attribute from `devices`. The connection to your device is then established the first time you call it from `usit.devices`. Further calls to it will use the Device instance created at the first call.
```python
usit.devices.tunics1
```
Now that you accessed a first time your device, a `[loaded]` flag is appended next to its name when you execute the commande `usit.devices`, which means that the device is connected.

Finally, you can access your variables, actions, sub-modules in this way:
```
usit.devices.tunics1.wavelength.set(1550)
wl = usit.devices.ltb1.power.get()
usit.devices.stage.goHome.do()
```

To close properly the connection to your device, simply execute the function `close` of the device: 
```python
usit.devices.tunics1.close()
```
Note that if you stored the object `usit.devices.tunics1` previously in a variable, this object is no longer usable, you need a new one from `usit.devices`. To close properly every connected devices, use the function `close_all` of the `usit.devices` object:
```python
usit.devices.close_all()
```



## Device modelization
___

In USIT, three objects are used to model completely a device : the Variables, the Actions, and the Modules.  
- A Variable is a physical quantity that can be measured on your device. It can be also editable, have a unit, etc. (for instance the wavelength of a light source, or the power of a power meter). In USIT, a Variable is then defined by its type (int, float, bool,...) and the functions in the associated driver that allows to interact with it.  
- An Action is basically a function in the driver that performs a particular action in the device, for instance making a stage going home. In USIT, an Action is defined by this function.  
- For a simple device, a Module represent the device itself, and has its own Variables and Actions in USIT. It can also have some sub-modules: in case that the device is a controller in which several sub-devices can be plugged or connected (for instance a power meter with several inputs, a motion controller with different stages,..), each sub-devices is also considered as a Module in USIT, which are themselves linked to a parent Module.

Example of the modules architecture:
```
Module "yenista_tunics"
   |-- Variable "wavelength"     (float, get and set functions)
   |-- Variable "power"          (float, get and set functions)
   |-- Action "turn_off"         (do function)
   
Module "yenista_osics"
   |-- Module "sld"
       |-- Variable "power"      (float, get and set functions)
       |-- Variable "output"     (bool, get and set functions)
   |-- Module "t100"
       |-- Variable "power"      (float, get and set functions)
       |-- Variable "output"     (bool, get and set functions)

Module "signalrecovery_lockin"
   |-- Variable "time_constant"     (float, get and set functions)
   |-- Variable "amplitude"         (float, only get function)
```

During the instantiation of a driver, an empty Module object is created in USIT, and represent at first the general device. The above modelization is then carried out using a python script *usit_config.py*, as explained below.


## USIT configuration
___

To work properly, you need to setup a few things :
1. Have a drivers folder on your computer
2. Create a *Device Index* file
3. Update a USIT *config.ini* file

### 1) Drivers folder

The drivers folder is the folder that contains all the drivers that USIT will use. It has a minimum required structure. Inside this main folder, each different driver need its own sub-folder. Ideally, the name of the sub-folder should be of the form *\<manufacturer\>\_\<model\>*. Then, inside this driver sub-folder, USIT requires at least two python scripts:  
- A driver script, which has the exact same name as the folder (*\<manufacturer\>\_\<model\>.py* for instance)
- A USIT configuration script, named *usit_config.py*, which allows the package to understand how your driver is structured in terms of Modules, Variables and Actions.

Example of drivers folder architecture:

```
-- drivers 
   |-- yenista_tunics
       |-- yenista_tunics.py
       |-- usit.config.py
   |-- exfo_ltb1
       |-- exfo_ltb1.py
       |-- usit.config.py
```

Note that our team is providing a lot of different drivers following this structure on our GitHub repository: https://github.com/bgarbin/toniq

#### "driver.py" script
USIT need a minimal driver structure. A class `Device` has to be present in each python driver script with an `__init__` function with only optional arguments (address, port, ...). These keywords arguments (kwargs) will be supplied by USIT during the instantiation of the driver, based on the information located in the Device Index file (see below). When instantiated, this class Device has to establish directly a connection with the device (with informations passed through the optional arguments of the `__init__` function), and hold it. This class `Device` should also have a function `close` to close properly the connection to the device. It is this function that is called when using `close` and `close_all` functions in USIT.

Example of a driver script :
```python
import visa

class Device():
    
    def __init__(self,address='GPIB0::9::INSTR'):
        
        self.TIMEOUT = 1000 #ms
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.TIMEOUT
        
    def close(self):
        try : self.controller.close()
        except : pass
```


#### 1) *usit_config.py* script
In this file, the user has to write a `configure` function that will be called after the instantiation of the driver, to model the device in USIT. This function has to take two arguments : a instance of the previous `Device` class just after its instantiation, and an instance of an empty and raw USIT Module object. The purpose of this function is to configure this Module by creating and associating `Variables`, `Actions`, `Modules`, and configure them with the functions of the `Device` object.

Example of *usit_config.py* :
```python
def configure(devDriver,devUsit):
   
    devUsit.addVariable('amplitude',float,
                        getFunction=devDriver.getAmplitude,
                        setFunction=devDriver.setAmplitude,
                        unit='V')
    
    devUsit.addAction('sth',
                        function=devDriver.doSth)
```
```python
def configure(devDriver,devUsit):
    
    sld = devUsit.addSubDevice('sld')    
    
    sld.addVariable('wavelength',float,
                        setFunction=devDriver.sld.setWavelength)
    
    sld.addVariable('power',float,
                        setFunction=devDriver.sld.setPower,
                        getFunction=devDriver.sld.getPower)
    
    t100 = devUsit.addSubDevice('t100')

    t100.addVariable('wavelength',float,
                        setFunction=devDriver.t100.setWavelength,
                        getFunction=devDriver.t100.getWavelength)
    
    t100.addVariable('frequency',float,
                        setFunction=devDriver.t100.setFrequency,
                        getFunction=devDriver.t100.getFrequency)
    
```  

### 2) *Device Index* file 

The Device Index configuration file contains the representation of the devices that are connected to your computer. It contains their name, the driver they need, their local connection informations (address, port, ...). The file need an .ini extention (e.g *devices_index.ini*) and can be located at any place in your computer (near your drivers folder for instance). This file is structured with several sections, each of them representing a physical device. The name of each sections corresponds to the name that will be used in USIT to communicate with the device, so it has to be unique. In each sections, the keyword `driver` is required and must indicate the name of a driver located in the drivers folder. Any other (keyword,value) pair (connection informations...) in the section will be sent as kwargs when instantiating the class `Device` of a driver.

Note that you can configure several devices using the same driver (in case several identical devices are connected to your computer).

Example of *devices_index.ini*:
```
[ltb1]
driver = exfo_ltb1
address = 192.168.0.97
port = 5024

[osics]
driver = yenista_osics
address = GPIB0::15::INSTR

[tunics1]
driver = yenista_tunics
address = GPIB0::10::INSTR

[tunics2]
driver = yenista_tunics
address = GPIB0::9::INSTR
```


### 3) USIT configuration file

As presented in the Quick Start section of the readme, USIT need to know about your devices and your drivers. At the first import of USIT in a Python console, a *config.ini* file is generated in your home directory, but contains default values which are likely to be wrong for you. You then have to update this config.ini file.  

In this configuration file, two paths have to be provided:
- `DriversPath` : this is the path to your drivers folder (see step 1).
- `DevicesIndexPath` : this is the path to the device configuration file (see step 2).

Example of *config.ini*:
```
[paths]
DriversPath = C:\Users\qchat\Documents\GitHub\toniq
DevicesIndexPath = C:\Users\qchat\Documents\GitHub\local_config\devices_index.ini
```

Remarks:
- If you accidentally remove the *config.ini* file or the *usit* folder from your home directory, they will be re-generated when importing usit again (but with default values).
- The values of an existing config.ini file will never be modified by USIT, so you won't have to modify it after update of this package.
