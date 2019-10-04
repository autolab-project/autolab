# toniq
Python3 based codes to drive your lab instruments.

Bruno Garbin and Quentin Chateiller, C2N-CNRS (Centre for Nanosciences and Nanotechnologies), Palaiseau, France


- (WINDOWS) install pywin32
- Recquiered python modules: vxi11, pyvisa, pyvisa-py, pyusb

Notes:
- Some of the codes are very basic and/or in test phase => please report problems/suggestions
- Be sure to have all the necessary python libraries
    notably: appropriate GPIB libraries for your OS (linux-gpib for linux), matplotlib, numpy, scipy, time, math, ...
- Have a look on Prog_Manual folder if you want to implement your own functions and help improve the repository
- __See drivers creation guidelines in GUIDELINES.md__
- See the __usit__ python package to automate your lab experiments : https://pypi.org/project/usit/ (dev ongoing)
