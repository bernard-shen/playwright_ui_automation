# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 安装Node.js和npm（用于Allure）
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# 安装Allure命令行工具
RUN npm install -g allure-commandline

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium
RUN playwright install-deps chromium

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p test_reports/logs test_reports/screenshot test_reports/report test_reports/allure-report

# 设置环境变量
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# 暴露端口（如果需要）
EXPOSE 8080

# 设置默认命令
CMD ["python", "run_web_ui_test.py"] 