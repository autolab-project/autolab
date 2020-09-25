:: Set the working directory back after running as administrator
@setlocal enableextensions
@cd /d "%~dp0"
:: Launch server
python ".\server.py"
pause