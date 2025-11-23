@echo off
chcp 65001 > nul
echo Запуск тестов...
pip install -r requirements.txt
python -m pytest tests/ -v
pause