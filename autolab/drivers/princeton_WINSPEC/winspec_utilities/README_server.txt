This package allows to control remotely the GUI Winspec interface.
A server is created on the HOST computer (where Winspec is running), listening for commands from a REMOTE computer through a local network

On the HOST comptuter : 
1) Install python 2.7.13 or 3
2) Install paths in variable environment : Path - C:\Python27;C:\Python27\scripts;
3) Command line : pip install pywinauto
4) Command line : pip uninstall comtypes
5) Command line : pip install pandas (>0.21)

Important : 
- The HOST computer has to be in the same local network as the REMOTE computer, with both an IP starting with "192.168.0.xxx". The detection of the IP address of the HOST computer is automatic when the server starts.
- The listened port is 5005.
- Only one connection at a time. If another REMOTE computer establishes a connection with the server, the previous connection will be automatically cancelled.

To launch the server :
1) Turn on winspec, make sure no subwindows are opened.
2) Close other windows, other softwares.
3) Execute "launcher.bat" AS ADMINISTRATOR to start the server
4) Send commands to 192.168.0.xxx at port 5005.


v1.1 15/07/2019
- Autodetection of the HOST computer local IP address (begining by a given prefix).
- The server has to be run as administrator to control winspec. Mofidied launcher.bat (you have to run it as admin)
- Check if winspec is well detected during launching procedure
- Partial display of spectrum data in the console (before : full display of the spectrum!)
- Commands management moved from winspec.py to server.py


v1.0 15/07/2019
- First upload

