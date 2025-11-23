@echo off
echo Сборка EXE-файла...
pyinstaller --onefile --windowed --name "CurrencyAnalysis" main.py
echo.
echo Если сборка успешна, EXE-файл будет в папке dist/
pause