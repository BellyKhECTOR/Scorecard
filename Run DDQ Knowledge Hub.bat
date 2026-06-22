@echo off
cd /d "%~dp0"
setlocal EnableDelayedExpansion

echo ============================================
echo  Mazi BD DDQ Knowledge Hub
echo ============================================
echo.

REM Check uv
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: uv is not installed or not in PATH.
    echo Install from https://docs.astral.sh/uv/
    pause
    exit /b 1
)
echo [OK] uv found

REM Check .env
if not exist ".env" (
    echo ERROR: .env file not found.
    echo Copy .env.example to .env and configure your settings.
    pause
    exit /b 1
)
echo [OK] .env found

REM Check required files
if not exist "pyproject.toml" (
    echo ERROR: pyproject.toml not found.
    pause
    exit /b 1
)
if not exist "app\main.py" (
    echo ERROR: app\main.py not found.
    pause
    exit /b 1
)
echo [OK] Required project files found

REM Install dependencies
echo.
echo Installing dependencies...
uv sync
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

REM Run migrations
echo.
echo Running database migrations...
uv run alembic upgrade head
if %ERRORLEVEL% neq 0 (
    echo ERROR: Database migration failed.
    echo Check DATABASE_URL in .env and ensure PostgreSQL is running.
    pause
    exit /b 1
)

REM Seed topics
echo.
echo Initialising topics...
uv run python scripts/initialise_topics.py
if %ERRORLEVEL% neq 0 (
    echo WARNING: Topic initialisation failed. Continuing...
)

REM Start server
echo.
echo Starting Mazi BD DDQ Knowledge Hub...
set APP_HOST=127.0.0.1
set APP_PORT=8000

REM Read host/port from .env if set
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    if "%%a"=="APP_HOST" set APP_HOST=%%b
    if "%%a"=="APP_PORT" set APP_PORT=%%b
)

echo Server URL: http://!APP_HOST!:!APP_PORT!
echo.

REM Open browser
start http://!APP_HOST!:!APP_PORT!

REM Start uvicorn (this blocks)
uv run uvicorn app.main:app --host !APP_HOST! --port !APP_PORT!
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo.
    echo ERROR: Application exited with code %EXIT_CODE%
    pause
)

exit /b %EXIT_CODE%
