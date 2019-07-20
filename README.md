# Usit
Universal Scanning Interface : python automation package for scientific experiments

by Quentin Chateiller, C2N (Center for Nanosciences and Nanotechnlogies), Palaiseau, France


## Quick start :
(To get a fine understanding of this quick start, you will have to read also the other parts of this readme file.)

First of all make sure that the directory usit is in your python path.  
Open a Python terminal and import usit and check what are the availables devices:
```
import usit
print(usit.devices)
print(usit.devices.get_available_devices())
```
This is a list of the devices found in the devices_index.txt, whose the driver name refers to a valid driver structure.
The connection to your device is established the first time you call it:
```
usit.devices.tunics1
```
Any further call to the device use the instantiation created at the first call.
Then access your variables, actions, sub-modules in this way:
```
usit.devices.tunics1.wavelength.set(1550)
wl = usit.devices.ltb1.power.get()
usit.devices.stage.goHome.do()
```



## Device modelization :

In USIT, three objects are used to model completely a device : the Variables, the Actions, and the Modules.  
- A Variable is a physical quantity that can measured on your device. It can be also editable, have a unit, etc. (for instance the wavelength of a light source, or the power of a power meter). In USIT, a Variable is then defined by its type (int, float, bool,...) and the function in the associated driver that allows to interact with it.  
- An Action is basically a function in the driver that performs a particular action in the device, for instance making a stage going home. In USIT, an Action is defined by this function.  
- For a simple device, a Module represent the device itself, and has its own Variables and Actions in USIT. It can also have some sub-modules: in case that the device is a controller in which several sub-devices can be plug or connected (for instance a power meter with several inputs, a motion controller with different stages,..), each sub-devices is also considered as a Module in USIT, which are themselves linked to a parent Module.

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

During the instantiation of a device, a empty Module object is created in USIT, and represent at first the device itself. The above modelization is then carried out using a python script "usit_config.py" that has to be present in the driver folder, as explained below.


## Configuration :
Before starting to use USIT, you have to configure paths in the file config.ini located in the folder config of this package.  
- DriversPath : path to your drivers folder. The needed driver folder architecture is specified in the toniq GitHub repository : https://github.com/bgarbin/toniq  
- DevicesIndexPath : path to the device configuration file. This file must contains informations about the devices locally connected, their driver, and all required information (arguments) to instantiate the driver.

Example of config.ini:
```
[paths]
DriversPath = C:\Users\qchat\Documents\GitHub\toniq
DevicesIndexPath = C:\Users\qchat\Documents\GitHub\local_config\devices_index.ini
```

### Device index (devices_index.ini for instance)
This .ini file is structured with several sections, each of them representing a physical device. The name of each sections has to be unique, and will be used in USIT to communicate with the device. In each sections, the keyword "driver" is required and must be equal to which has to refer to a correct driver name in the driver folder path specified (DriversPath) in the configuration file. Any other (keyword,value) couple (address, port, ...) of the section will be sent to the driver as kwargs in the init function of the Device class (see below).

Example of devices_index.ini:
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



## Driver structure :

Driver folder whose the path has been provided in the file drivers_path.txt need a minimum following structure. Each driver need its own folder. In the toniq repository, each folder name has the form "\<manufacturer\>\_\<model\>". In this driver folder, USIT requires at least two pyhon scripts:
- A driver script, which the exact same name as the folder : "\<manufacturer\>\_\<model\>.py" for instance
- A usit configuration script, name "usit_config.py", which allow USIT to understand how your driver is structured in terms of Modules, Variables and Actions.

Example of drivers folder architecture:

```
-- toniq 
   |-- yenista_tunics
       |-- yenista_tunics.py
       |-- usit.config.py
   |-- exfo_ltb1
       |-- exfo_ltb1.py
       |-- usit.config.py
```


### driver.py
USIT need a minimal driver structure. A class "Device" has to be present in each python driver script with an \_\_init\_\_ function that requires the address (str) of the device as first argument. This address will be supplied by USIT during the instantiation (based on the information located in the file devices_index.txt). Based on the provided address, this \_\_init\_\_ function also have to establish directly a connection with the device, and hold it. This class "Device" should have a function "close" to close properly the connection to the device. 

Example of a driver script :
```
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


### usit_config.py
In this file, the user has to write a "configure" function that will be called by USIT to modelize the device. This function has to take two arguements : a raw instance of the "Device" class located in the driver script (device newly connected), and an instance of an empty and raw USIT Module object. The purpose of this function is to configure this Module object by creating Variables, Actions, (sub-Modules) and configure them with the driver instance functions.

Example of usit_config.py :
```
def configure(devDriver,devUsit):
   
    devUsit.addVariable('amplitude',float,
                        getFunction=devDriver.getAmplitude,
                        setFunction=devDriver.setAmplitude,
                        unit='V')
    
    devUsit.addAction('sth',
                        function=devDriver.doSth)
```
```
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




