@echo off
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "ScriptExplorer" /f
if %errorlevel%==0 (
    echo [OK] Автозапуск удалён.
) else (
    echo [INFO] Запись не найдена — возможно, уже удалена.
)
pause
