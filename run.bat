@echo off
chcp 65001 > nul
title Mi Control de Finanzas Personales

echo ======================================================================
echo           INICIANDO MI CONTROL DE FINANZAS PERSONALES
echo ======================================================================
echo.

:: Detectar intérprete de Python (probar 'py' y luego 'python')
where py >nul 2>nul
if %errorlevel% equ 0 (
    set PY_CMD=py
    goto :RUN_APP
)

where python >nul 2>nul
if %errorlevel% equ 0 (
    set PY_CMD=python
    goto :RUN_APP
)

echo [ERROR] No se encontró Python instalado en este equipo.
echo Por favor descarga e instala Python desde https://www.python.org/downloads/
echo Asegúrate de marcar la casilla "Add python.exe to PATH" durante la instalación.
echo.
pause
exit /b 1

:RUN_APP
echo Verificando dependencias necesarias...
%PY_CMD% -c "import streamlit, pandas, plotly, openpyxl" >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando paquetes requeridos por primera vez (esto toma solo un momento)...
    %PY_CMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Ocurrió un inconveniente instalando las dependencias.
        pause
        exit /b 1
    )
)

echo Lanzando aplicación en el navegador web...
%PY_CMD% run.py
if %errorlevel% neq 0 (
    echo.
    echo Ocurrió un error inesperado al cerrar la aplicación.
    pause
)
