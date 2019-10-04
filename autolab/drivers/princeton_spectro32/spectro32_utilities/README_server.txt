This package allows to control remotely a princeton Acton SP2500 spectrometer.
A server is created on the HOST computer (where the actual communication takes place), listening for commands from a REMOTE computer through a local network

On the HOST comptuter : 
1) Install python 2.7.13 or 3
2) Install paths in variable environment : Path - C:\Python27;C:\Python27\scripts;

Important : 
- The HOST computer has to be in the same local network as the REMOTE computer, with both an IP starting with "192.168.0.xxx". The detection of the IP address of the HOST computer is automatic when the server starts.
- The listened port is 5005.
- Only one connection at a time. If another REMOTE computer establishes a connection with the server, the previous connection will be dropped automatically.

To launch the server :
1) Stop acquisition through Winspec (if using it)
2) Execute "launcher.bat" to start the server
3) Send commands to 192.168.0.xxx at port 5005.

