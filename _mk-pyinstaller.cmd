@echo off


SET DIR=App
rd %DIR% /s /q
rd build /s /q

C:\Python27\Scripts\pyinstaller main.py --distpath %DIR% --onefile --noconsole --key=what=ever-key-you-want --win-private-assemblies --win-no-prefer-redirects


rem copy needed files
copy *.rsrc.py %DIR%\ 
copy *.ini %DIR%\ 
copy *.ico %DIR%\
copy *.json %DIR%\


pause
