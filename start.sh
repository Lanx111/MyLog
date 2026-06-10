#!/bin/bash
# MyLog - 一键启动前后端服务
# 使用方法: bash start.sh

echo "========================================"
echo "  MyLog - 个人主页与成长日志系统"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 启动后端
echo "[1/2] Starting backend (FastAPI) on port 8000..."
cd "$SCRIPT_DIR/backend"
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
python init_db.py 2>/dev/null  # 首次运行建表 + 种子数据，已有数据则跳过
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"
sleep 2

# 启动前端
echo "[2/2] Starting frontend (Vite + React) on port 5173..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID"
sleep 3

echo ""
echo "========================================"
echo "  Services started!"
echo ""
echo "  打开浏览器访问: http://localhost:5173"
echo "  API 文档:        http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C, then kill both
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
