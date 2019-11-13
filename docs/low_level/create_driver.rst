.. _create_driver:

Create your own Driver
======================

**   !!!! OLD VERSION !!!! **


# Driver creation guidelines

The goal of this tutorial is to present the general structure of the drivers of this GitHub repository, in order for you to create your own drivers based on this structure, and make them available in this repository.

This package provides a set of standardized drivers for about 40 instruments (for now) which are ready to use, and is open to inputs from the community (new drivers or upgrades of existing ones)
To help you writting your own drivers, a few templates are provided on the `GitHub page of the project <https://github.com/qcha41/autolab/tree/master/autolab/drivers/More/Templates>`_.

## Directory organization

Each different device has its own folder in this repository. The name of this folder take the form *\<manufacturer\>_\<model\>*. The driver associated to this device is a python script taking the same name as the folder: *\<manufacturer\>_\<model\>.py*. There can be additional python scripts in this folder (devices's modules, ..).

## Driver script

### Device class

Inside the driver script, a driver is basically represented by a class `Device`. This class can be view as a "cooking recipe" that explains to Python how to interact with your device. But in order to interact with it effectively, we need to create an instance of this class (like making a cake from a recipe), and to store it in a variable (for example `my_device`):

```python
class Device() :
    def __init__(self):
        pass
        
my_device = Device()
```

### Controller

First of all, we have to configure a first attribute in this class: the controller. This will be the object through which we are communicating with the device. In most cases, you will use the python package `visa` for GPIB, SERIAL, USB connections (see its documentation). You can also use the packages `telnet` or `socket` for ETHERNET communications.  

In any case, the controller needs the address of your device to establish a connection with it. With `visa`, you can get the available addresses we these three lines of codes:

```python
import visa
rm = visa.ResourceManager()
rm.list_resources()
```
Just execute it before and after plugging your device to see which address appeared. 

For ethernet connections, you should know the IP address (set it to be part of your local network) and the port (device documentation) of your device.   

This address is provided when we instantiate the device, but we store a default value in a variable `ADDRESS`.

```python
import visa

ADDRESS = 'GPIB0::8::INSTR'

class Device() :
    def __init__(self,address=ADDRESS):
        rm = visa.ResourceManager()
        self.controller = rm.open_resources(address)
        
my_device = Device() # Use the default address
my_device = Device(address='GPIB0::3::INSTR') # Use the given address
```
At this point, you are connected to your device as soon as you create an instance of the class Device.

### Close function
We recommand to create a class function `close` to be able to close properly the connection to your device.

```python
import visa

ADDRESS = 'GPIB0::8::INSTR'

class Device() :
    def __init__(self,address=ADDRESS):
        rm = visa.ResourceManager()
        self.controller = rm.open_resources(address)
        
    def close(self):
        self.controller.close()
        
my_device = Device() 
print('Connection established')
my_device.close()
print('Connection closed')
```

You can know create a connection to your device, and close it properly.

### Query / Write / Read functions

We now have to create interaction functions such as `write`, `query` or `read`. These functions already exists in `visa`.

```python
import visa

ADDRESS = 'GPIB0::8::INSTR'

class Device() :
    def __init__(self,address=ADDRESS):
        rm = visa.ResourceManager()
        self.controller = rm.open_resources(address)
        
    def close(self):
        self.controller.close()
        
    def query(self,command):
        return self.controller.query(command)
        
    def write(self,command):
        self.controller.write(command)
        
    def read(self):
        return self.controller.read()
        
my_device = Device() 
```

We are now able to send commands and get results to our devices. Let's now define the functions associated to these commands.

### Device functions

The last thing to do is to create the class functions that we will need to set a parameter, to get its value, or to process an action. This depends of course of your device, have a look on your user manual to see the available commands.

```python
import visa

ADDRESS = 'GPIB0::8::INSTR'

class Device() :
    def __init__(self,address=ADDRESS):
        rm = visa.ResourceManager()
        self.controller = rm.open_resources(address)
        
    def close(self):
        self.controller.close()
        
    def query(self,command):
        return self.controller.query(command)
        
    def write(self,command):
        self.controller.write(command)
        
    def read(self):
        return self.controller.read()
        
        
    def setWavelength(self,value):
        self.write(f'NM={value}')
        self.query('*OPC?') # Wait until the device says the operation is done
        
    def getWavelength(self):
        return self.query('NM?')
        
        
    def setPower(self,value):
        self.write(f'PW={value}')
        self.query('*OPC?') # Wait until the device says the operation is done
        
    def getPower(self):
        return self.query('PW?')
        
        
    def goHome(self):
        self.write('HOME')
        self.query('*OPC?') # Wait until the device says the operation is done
        
        
my_device = Device() 
print(my_device.getWavelength()) # Returns the current value of the wavelength, for instance 1540
my_device.setWavelength(1550)
print(my_device.getWavelength()) # Returns 1550
```


### The device is a controller

The device you are working with may be a controller that contains several instruments, or stages, or channels, etc.. To communicate with these sub-modules, we usually need a "slot" information in the command. To take into account these sub-modules, and to avoid a redondant `Device` class, we create additional classes located in additional python script, that will be imported in the main driver script:

[ Folder architecture ] 
```
manufacturer_model
    |-- manufacturer_model.py
    |-- moduleA.py
    |-- moduleB.py
```


[ moduleA.py ]

```python

class ModuleA() :
    def __init__(self,driver,slot):
        self.driver = driver
        self.slot = slot
        self.prefix = f'CH{slot}'
        
    def query(self,command):
        return self.driver.query(self.prefix+command)
        
    def write(self,command):
        self.driver.write(self.prefix+command)
        
    def read(self):
        return self.driver.read()
        
    def setWavelength(self,value):
        self.write(f'NM={value}')
        self.query('*OPC?') # Wait until the device says the operation is done
        
    def getWavelength(self):
        return self.query('NM?')
        
```

[ moduleB.py ]

```python

class ModuleB() :
    def __init__(self,driver,slot):
        self.driver = driver
        self.slot = slot
        self.prefix = f'CH{slot}'
        
    def query(self,command):
        return self.driver.query(self.prefix+command)
        
    def write(self,command):
        self.driver.write(self.prefix+command)
        
    def read(self):
        return self.driver.read()
        
    def setPower(self,value):
        self.write(f'PW={value}')
        self.query('*OPC?') # Wait until the device says the operation is done
        
    def getPower(self):
        return self.query('PW?')
        
```

[ manufacturer_model.py ]
```python
import visa
from moduleA import ModuleA
from moduleB import ModuleB

ADDRESS = 'GPIB0::8::INSTR'

class Device() :
    def __init__(self,address=ADDRESS):
        rm = visa.ResourceManager()
        self.controller = rm.open_resources(address)
        
        self.slot1 = ModuleA(self,1)
        self.slot2 = ModuleB(self,2)
        
    def close(self):
        self.controller.close()
        
    def query(self,command):
        return self.controller.query(command)
        
    def write(self,command):
        self.controller.write(command)
        
    def read(self):
        return self.controller.read()

        
        
my_device = Device() 
my_device.slot1.getWavelength()
my_device.slot2.setPower(0.2)
```

The previous structure should be used only if the physical slot configuration is naturally fixed by the manufacturer (a power meter with two channels for instance). In some cases, this slot configuration can change between two devices of the same model (module racks that can be place at different slot in the controller..). To take this into account, all information about the slot configuration should be provided in argument when instantiating the `Device` class for a dynamical slot attribute creation, following this structure:

[ manufacturer_model.py ]
```python
import visa
from moduleA import ModuleA
from moduleB import ModuleB

ADDRESS = 'GPIB0::8::INSTR'

modules_dict = {'modA':ModuleA,'modB':ModuleB}

class Device() :
    def __init__(self,address=ADDRESS):
        rm = visa.ResourceManager()
        self.controller = rm.open_resources(address)
        
        # Submodules generation
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = modules_dict[ kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                setattr(self,name,module(self,slot_num))

        
    def close(self):
        self.controller.close()
        
    def query(self,command):
        return self.controller.query(command)
        
    def write(self,command):
        self.controller.write(command)
        
    def read(self):
        return self.controller.read()

        
        
my_device = Device(slot1='modA,my_moduleA_1',         # Module physically in slot 1
                    slot2='modA,my_moduleA_2',        # Module physically in slot 2
                    slot5='modA,my_moduleB')          # Module physically in slot 5
my_device.my_moduleA_1.getWavelength()
my_device.my_moduleA_2.setWavelength(1550)
my_device.my_moduleB.setPower(0.2)
