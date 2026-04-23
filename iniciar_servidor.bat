@echo off
title BaixaTube - Servidor
color 0C

echo.
echo  ========================================
echo   BAIXATUBE - Servidor Local
echo  ========================================
echo.

:: Vai para a pasta do servidor
cd /d "%~dp0servidor"

:: Inicia o servidor com o Python correto
echo  Iniciando servidor em localhost:9999...
echo  Pressione Ctrl+C para parar.
echo.

C:\Users\LGLOB\AppData\Local\Python\pythoncore-3.14-64\python.exe servidor.py

echo.
echo  Servidor encerrado.
pause
