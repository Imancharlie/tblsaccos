@echo off
echo ========================================
echo TBL SACCOS Deployment Script
echo ========================================
echo.

echo Checking Django configuration...
python manage.py check
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Django check failed. Please fix the issues before deploying.
    pause
    exit /b 1
)

echo.
echo Running database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Migrations failed. Please check the database connection.
    pause
    exit /b 1
)

echo.
echo Collecting static files...
python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Static file collection failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Deployment completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Upload your project to PythonAnywhere
echo 2. Configure the WSGI file with your username
echo 3. Set up static files in PythonAnywhere
echo 4. Reload your web app
echo.
echo See PYTHONANYWHERE_DEPLOYMENT.md for detailed instructions
echo.
pause
