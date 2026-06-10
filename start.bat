@echo off
REM MyLog - 一键启动前后端服务 (Windows)
REM 使用方法: 双击 start.bat 或在终端运行 start.bat

echo ========================================
echo   MyLog - Personal Homepage ^& Growth Log
echo ========================================
echo.

set SCRIPT_DIR=%~dp0

REM 启动后端
echo [1/2] Starting backend (FastAPI) on port 8000...
cd /d "%SCRIPT_DIR%backend"
call venv\Scripts\activate.bat
python init_db.py 2>nul
start "MyLog-Backend" cmd /k "cd /d %SCRIPT_DIR%backend && venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8000"

REM 启动前端
echo [2/2] Starting frontend (Vite + React) on port 5173...
cd /d "%SCRIPT_DIR%frontend"
start "MyLog-Frontend" cmd /k "cd /d %SCRIPT_DIR%frontend && npm run dev"

timeout /t 5 >nul

echo.
echo ========================================
echo   Services started!
echo.
echo   Open browser: http://localhost:5173
echo   API docs:     http://localhost:8000/docs
echo ========================================
echo.
echo Close the two popup windows to stop services.
pause
