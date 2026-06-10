# ---- MyLog Backend: FastAPI + SQLite ----
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制源码
COPY *.py .
COPY routers/ ./routers/

# 数据持久化目录
RUN mkdir -p /app/data
ENV DATABASE_URL=sqlite:////app/data/mylog.db

# 启动脚本
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]
