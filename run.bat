@echo off
title XboxConnexion - 3D SpaceMouse CAD Controller
cd /d "%~dp0"
echo ===================================================
echo     XboxConnexion - 3D SpaceMouse CAD Controller   
echo ===================================================
echo.
python src\main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application closed with code %ERRORLEVEL%.
    pause
)
