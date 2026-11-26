@echo off
chcp 65001 >nul
title Importar datos de "Reels Sundesign"
cd /d "%~dp0"
echo.
echo   Copia tus videos, productos, estilos, musica y sugerencias desde la carpeta
echo   anterior "Reels Sundesign" a esta carpeta. NO borra nada: la carpeta vieja queda igual.
echo.
set "ORIGEN="
if exist "%USERPROFILE%\Documents\Reels Sundesign\trabajos" set "ORIGEN=%USERPROFILE%\Documents\Reels Sundesign"
if exist "%USERPROFILE%\OneDrive\Documents\Reels Sundesign\trabajos" set "ORIGEN=%USERPROFILE%\OneDrive\Documents\Reels Sundesign"
if exist "%USERPROFILE%\OneDrive\Documentos\Reels Sundesign\trabajos" set "ORIGEN=%USERPROFILE%\OneDrive\Documentos\Reels Sundesign"
if "%ORIGEN%"=="" (
  echo   No encontre la carpeta "Reels Sundesign" en Documentos.
  echo   Si la tenes en otro lugar, copia a mano sus carpetas trabajos, estilos, productos, musica y sugerencias aca.
  pause
  exit /b
)
echo   Encontre: %ORIGEN%
echo   Cerra la "App Sundesign" antes de seguir.
pause
for %%D in (trabajos estilos productos musica sugerencias) do (
  if exist "%ORIGEN%\%%D" robocopy "%ORIGEN%\%%D" "%~dp0%%D" /E /XC /XN /XO /NFL /NDL /NJH /NJS >nul
)
echo.
echo   Listo. Abri la App y revisa que esten tus videos.
echo   Cuando confirmes que esta todo, podes borrar a mano la carpeta vieja (es opcional).
pause
