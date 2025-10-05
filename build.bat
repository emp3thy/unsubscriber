@echo off
echo Building Email Unsubscriber standalone executable...

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Check if all requirements are installed
echo Checking dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements
    pause
    exit /b 1
)

REM Build the executable
echo Building executable...
pyinstaller build.spec --clean

REM Check if build succeeded
if exist "dist\EmailUnsubscriber\EmailUnsubscriber.exe" (
    echo Build successful!
    echo.
    echo The executable is located at: dist\EmailUnsubscriber\EmailUnsubscriber.exe
    echo Size: %~z1 bytes
    echo.
    echo You can now distribute this file to other Windows computers.
    echo Note: The executable requires Windows and does not need Python installed.
) else (
    echo Build failed!
    echo Check the console output above for errors.
)

echo.
pause
