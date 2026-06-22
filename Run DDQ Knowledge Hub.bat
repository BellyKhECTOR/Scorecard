@echo off
cd /d "%~dp0"
setlocal EnableDelayedExpansion

echo ============================================
echo  Mazi BD DDQ Knowledge Hub
echo  Universe folder: BD - DDQ
echo ============================================
echo.
echo Project folder: %CD%
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
    echo.
    echo Expected project folder:
    echo   C:\Users\KhotsoMokoatle\OneDrive - Mazi\Desktop\Projects\Universe\BD - DDQ
    pause
    exit /b 1
)
echo [OK] .env found

REM Check required files
if not exist "pyproject.toml" (
    echo ERROR: pyproject.toml not found.
    echo Make sure you are running this from the BD - DDQ project folder.
    pause
    exit /b 1
)
if not exist "app\main.py" (
    echo ERROR: app\main.py not found.
    pause
    exit /b 1
)
echo [OK] Required project files found

REM Ensure data directories exist
if not exist "data\backlog" mkdir "data\backlog"
if not exist "data\inbox" mkdir "data\inbox"
if not exist "data\reports" mkdir "data\reports"
if not exist "sample_documents" mkdir "sample_documents"
echo [OK] Data folders ready

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

REM Start server — always localhost only
echo.
echo Starting Mazi BD DDQ Knowledge Hub (local only)...
set APP_HOST=127.0.0.1
set APP_PORT=8000
set LOCAL_ONLY=true

REM Read port from .env if set (host stays 127.0.0.1 for security)
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    if "%%a"=="APP_PORT" set APP_PORT=%%b
)

echo.
echo Project:  %CD%
echo URL:      http://127.0.0.1:!APP_PORT!
echo Backlog:  %CD%\data\backlog
echo Inbox:    %CD%\data\inbox
echo.

REM Open browser
start http://127.0.0.1:!APP_PORT!

REM Start uvicorn (this blocks) — localhost only, never 0.0.0.0
uv run uvicorn app.main:app --host 127.0.0.1 --port !APP_PORT!
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo.
    echo ERROR: Application exited with code %EXIT_CODE%
    pause
)

exit /b %EXIT_CODE%
