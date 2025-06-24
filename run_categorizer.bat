@echo off
echo Starting Norwegian Company Categorizer...

REM Activate virtual environment
call myenv\Scripts\activate.bat

REM Set SSL verification to false for virtual desktops (uncomment if needed)
REM set SSL_VERIFY=false

REM Check if input file is provided
if "%1"=="" (
    echo Usage: run_categorizer.bat input_file.csv
    echo Example: run_categorizer.bat input\sample.csv
    pause
    exit /b 1
)

REM Run the categorizer
python categorize.py %1 %2 %3 %4 %5

REM Keep window open to see results
pause 