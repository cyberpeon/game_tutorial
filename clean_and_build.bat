@echo off
echo ==========================================
echo  Game Builder - Clean & Build
echo ==========================================

echo 1. Cleaning up old files...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist __pycache__ rd /s /q __pycache__
del *.spec
del *.exe

echo.
echo 2. Building games...
echo.

echo Building Fighting Game...
pyinstaller --onefile --windowed --name FightingGame fighting.py

echo Building Dodge Game...
pyinstaller --onefile --windowed --name DodgeGame dodge.py

echo.
echo 3. Finalizing...
move dist\*.exe .
rd /s /q build
rd /s /q dist
del *.spec

echo.
echo ==========================================
echo  Build Complete!
echo  You can now run the .exe files directly.
echo ==========================================
pause
