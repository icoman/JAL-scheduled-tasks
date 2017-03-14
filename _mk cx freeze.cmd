@echo off

rem
rem may need vc_redist_x86-2008
rem and also vcredist_x86-runtime-2010
rem



SET DIR=App
rd %DIR% /s /q
c:\Python27\python c:\Python27\Scripts\cxfreeze --install-dir=%DIR% main.py

rem copy needed files
copy *.rsrc.py %DIR%\
copy *.json %DIR%\
copy *.ico %DIR%\

rem remove unneeded folders
rd /s /q %DIR%\tcl
rd /s /q %DIR%\tk


pause
