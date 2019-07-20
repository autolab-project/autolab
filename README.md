# Usit
Universal Scanning Interface : python automation package for scientific experiments

by Quentin Chateiller, C2N (Center for Nanosciences and Nanotechnlogies), Palaiseau, France


## Minimum required directory tree architecture :
```
-- usit (this repository)  
-- local_config  
   |-- drivers_path.txt  
   |-- devices_index.txt  
```
   
##### drivers_path.txt
This file must contains the path to the driver folder in your computer (toniq repository for instance).
Example: C:\Users\qchat\Documents\GitHub\local_config
The needed driver folder architecture is specified in the toniq GitHub repository : https://github.com/bgarbin/toniq

Example:
```
C:\Users\qchat\Documents\GitHub\toniq
```

##### devices_index.txt
This file must contains information about the devices locally connected and their address.
Each line represent a device, and is made of three columns: name,driver,address (separated by commas). The name has to be unique.
- The first column is the name you want to give to your device in Usit. It has to be unique.
- The second column is the name of the associated driver, which has to refer to a correct driver name in the driver folder path specified in  drivers_path.txt
- The third column is the address of your device : GPIB::5::INSTR, 192.168.0.6, etc... It depends on your local device configuration and on what is expected by the Device class in the driver file, but it must be a string in all case.  

Example:
```
tunics1,yenista_tunics,GPIB::5::INSTR
tunics2,yenist_tunics,GPIB::6::INSTR
ltb1,exfo_ltb1,192.169.0.8
```
