@echo off
echo ========================================
echo SkillNova Database Migration Runner
echo ========================================
echo.

echo Step 1: Checking current setup...
echo.
python check_setup.py
echo.

echo Step 2: Running database migrations...
echo.

cd database
python run_migrations.py
cd ..

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Step 3: Verifying setup after migrations...
    echo.
    python check_setup.py
    echo.
    echo ========================================
    echo Migrations completed successfully!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Restart your backend server (Ctrl+C then python app.py)
    echo 2. Refresh your browser (Ctrl+Shift+R)
    echo 3. Test the admin pages
    echo.
) else (
    echo.
    echo ========================================
    echo Migration failed!
    echo ========================================
    echo.
    echo Please check:
    echo 1. PostgreSQL is running
    echo 2. Database credentials in backend/.env are correct
    echo 3. Database 'skillnova' exists
    echo.
)

pause
