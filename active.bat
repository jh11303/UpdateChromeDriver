@echo off

if not defined VENV_DIR (set "VENV_DIR=%~dp0%venv")

set PYTHON_EXE=python
set ERROR_REPORTING=FALSE

if exist tmp (
    echo tmp folder does exist. No need to create.
) else (
    echo Creating tmp folder...
    mkdir tmp 2>NUL
    if %ERRORLEVEL% neq 0 (
        echo Unable to create tmp folder. Exiting.
        pause
        exit /b
    )
    echo Create tmp folder successful.
)

goto :start_venv

:start_venv
if ["%VENV_DIR%"] == ["-"] goto :skip_venv
if ["%SKIP_VENV%"] == ["1"] goto :skip_venv

dir "%VENV_DIR%\Scripts\Python.exe" >tmp/stdout.txt 2>tmp/stderr.txt
if %ERRORLEVEL% == 0 goto :activate_venv

for /f "delims=" %%i in ('CALL %PYTHON_EXE% -c "import sys; print(sys.executable)"') do set PYTHON_FULLNAME="%%i"
echo Creating venv in directory %VENV_DIR% using python %PYTHON_FULLNAME%
%PYTHON_FULLNAME% -m venv "%VENV_DIR%" >tmp/stdout.txt 2>tmp/stderr.txt
if %ERRORLEVEL% == 0 goto :activate_venv
echo Unable to create venv in directory "%VENV_DIR%"
goto :show_stdout_stderr

:activate_venv
set PYTHON_EXE="%VENV_DIR%\Scripts\Python.exe"
echo venv %PYTHON_EXE%
goto :install_requirements

:skip_venv
goto :install_requirements

:install_requirements
echo Installing requirements...
%PYTHON_EXE% -m pip install -r requirements.txt %* > tmp\pip_output.txt 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR! An error occurred during installation. See the output below:
    type tmp\pip_output.txt
    pause
    exit /b
) else (
    echo Requirements installed successfully.
)

echo Updating vscode settings...
%PYTHON_EXE% update_settings.py

echo Vscode settings update completed.
echo Deployment successful.
exit /b

:show_stdout_stderr

echo.
echo exit code: %errorlevel%

for /f %%i in ("tmp\stdout.txt") do set size=%%~zi
if %size% equ 0 goto :show_stderr
echo.
echo stdout:
type tmp\stdout.txt

:show_stderr
for /f %%i in ("tmp\stderr.txt") do set size=%%~zi
if %size% equ 0 goto :endofscript
echo.
echo stderr:
type tmp\stderr.txt

:endofscript

echo.
echo Launch unsuccessful. Exiting.
pause