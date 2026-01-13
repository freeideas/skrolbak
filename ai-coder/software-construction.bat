@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

pushd "%PROJECT_ROOT%" >nul
set "PROJECT_ROOT_ABS=%CD%"
popd >nul

if not "%CD%"=="%PROJECT_ROOT_ABS%" (
    echo Please run this script from the project root:
    echo   cd %PROJECT_ROOT_ABS%
    exit /b 1
)

.\ai-coder\bin\uv.exe run --script .\ai-coder\scripts\software-construction.py %*