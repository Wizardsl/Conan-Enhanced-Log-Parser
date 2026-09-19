@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Conan Log Parser
where python >nul 2>nul
if %errorlevel%==0 (
    python parser.py
) else (
    py -3 parser.py
)
echo.
echo Parser stopped.
pause
