@echo off
chcp 65001 >nul
title App Sundesign - diagnostico
cd /d "%~dp0_programa\estudio-app"
echo.
echo   Abriendo la App Sundesign en modo diagnostico...
echo   Si aparece un error, sacale una captura a esta ventana y mandasela a Claude.
echo   (Si la app abre bien, deja esta ventana abierta mientras la usas.)
echo.
where py >nul 2>nul && (py app.py) || (python app.py)
echo.
echo   ---- La app se cerro. Captura de esta ventana para Claude ----
pause
