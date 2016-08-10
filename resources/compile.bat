set UI_PYTHON_PATH=../python/ui

:s_next
IF ["%1"] EQU [""] ECHO Done&exit

IF ["%~x1"] EQU [".ui"] CALL T:\dwtv\hub\Pipeline\thirdparty\Python-2.7.3_64\Scripts\pyside-uic.exe %1 -o %UI_PYTHON_PATH%/%~n1%_form.py

IF ["%~x1"] EQU [".qrc"] CALL T:\dwtv\hub\Pipeline\thirdparty\Python-2.7.3_64\Lib\site-packages\PySide-1.2.1-py2.7-win-amd64.egg\PySide\pyside-rcc.exe %1 -o %UI_PYTHON_PATH%/%~n1%_rc.py

SHIFT
GOTO :s_next
