@echo off
REM Double-click to launch the live draft assistant.
REM Closing this window stops the local server.
setlocal
cd /d "%~dp0"

set "PY="
where py >nul 2>nul
if not errorlevel 1 set "PY=py"
if defined PY goto run
where python >nul 2>nul
if not errorlevel 1 set "PY=python"
if defined PY goto run

echo.
echo   Python 3 was not found on PATH.
echo   Install it from https://www.python.org/downloads/
echo   and tick "Add python.exe to PATH" during setup.
echo.
pause
exit /b 1

:run
%PY% src\run.py --page draft %*
if errorlevel 1 pause
