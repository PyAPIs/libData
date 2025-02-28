@echo off
git clone https://github.com/PyAPIs/DataAPI

:: Check if the git clone was successful
if %ERRORLEVEL% neq 0 (
    echo Git clone failed. Please check you have git installed and you have permission to clone the repository.
    exit /b 1
)

cd DataAPI

for /f "delims=" %%f in ('dir /b /a-d') do (
    if /i not "%%f"=="DataManager.py" (
        del "%%f"
    )
)

for /d /r %%d in (*) do rd "%%d" 2>nul

timeout /t 2 >nul
del "%~f0"
