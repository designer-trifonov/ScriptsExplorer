@echo off
for /f "usebackq tokens=*" %%i in (`python -c "import sys,os;print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))"`) do set PYW=%%i
if "%PYW%"=="" (
    echo [ОШИБКА] pythonw.exe не найден. Убедитесь, что Python установлен.
    pause & exit /b 1
)
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" ^
    /v "ScriptExplorer" /t REG_SZ ^
    /d "\"%PYW%\" \"%~dp0main.py\"" /f
echo [OK] Автозапуск установлен: %PYW% %~dp0main.py
pause
