FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libxss1 \
    libasound2 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install chromium

# 复制代码
COPY admin_app.py .
COPY final_auto_upload_db_v3.py .
COPY database_doc.md .
COPY templates/ ./templates/
COPY database/schema.sql ./database/

# 创建上传目录
RUN mkdir -p uploads screenshots

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "admin_app.py"]
