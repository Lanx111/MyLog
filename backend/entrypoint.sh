#!/bin/bash
set -e

echo "[MyLog v2 Backend] Initializing database..."
python -c "
from database import engine, Base
Base.metadata.create_all(bind=engine)
print('Tables ready.')
"

# First run: create demo users (lanxin/zhangsan)
python init_db.py

echo "[MyLog v2 Backend] Starting API server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
