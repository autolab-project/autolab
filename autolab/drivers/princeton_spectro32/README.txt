This package is dedicated to control a spectrometer Acton SP2500 for remote control only.

The acquisition takes place on a HOST computer while the user sends commands from a REMOTE computer via a TCPIP server in a local network (192.168.0.***).

1. Move the content of the spectro32_server folder to your HOST computer and start the server following the instructions of the server README file.
2. Instantiate the class Device in the princeton_spectr32.py script located on the REMOTE computer.
