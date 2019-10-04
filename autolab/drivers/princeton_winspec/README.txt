This package is dedicated to control the GUI Winspec for remote control only.

Winspec is running on a HOST computer while the user controls it from a REMOTE computer.
The communication between the two use a TCPIP server on the HOST computer, which controls Winspec through the file winspec_gui_driver.py

1. Move the content of the winspec_server folder to your HOST computer and start the server following the instructions of the server README file.
2. Instantiate the class Device_SOCKET in the princeton_winspec.py script located on the REMOTE computer.