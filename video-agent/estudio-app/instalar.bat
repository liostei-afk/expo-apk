@echo off
chcp 65001 >nul
title Instalar Estudio de Reels - Sundesign
cd /d "%~dp0"
echo.
echo   ESTUDIO DE REELS - Sundesign Muebles
echo   ------------------------------------
echo.
where pyw >nul 2>nul
if %errorlevel%==0 goto tengo_python
where pythonw >nul 2>nul
if %errorlevel%==0 goto tengo_python
echo   No encontre Python en esta PC. Lo instalo (es gratis, tarda unos minutos)...
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
echo.
echo   Python quedo instalado. CERRA esta ventana y volve a abrir instalar.bat
echo   para terminar (Windows necesita reiniciar la ventana para encontrarlo).
pause
exit /b
:tengo_python
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0crear-acceso-directo.ps1" -dir "%~dp0."
echo.
echo   Abriendo el Estudio...
start "" pyw "%~dp0app.py" 2>nul || start "" pythonw "%~dp0app.py"
echo.
echo   Desde ahora abrilo con el icono "Estudio de Reels" del Escritorio.
timeout /t 6 >nul
