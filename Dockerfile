# 1. 基础环境：我们拿 Python 3.11 轻量版作为底子
FROM python:3.11-slim

# 2. 设置工作目录：进入容器后，自动 cd 到 /app 文件夹
WORKDIR /app

# 3. 先复制依赖清单（这一步是为了利用 Docker 缓存，下次构建更快）
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 5. 把当前电脑上所有的项目代码复制进容器的 /app 目录
COPY . .

# 6. 告诉别人这个容器用的是 8000 端口（只是说明，实际映射在 compose 里做）
EXPOSE 8000

# 7. 容器启动时运行的命令：用 uvicorn 启动你的 main.py
CMD ["python", "-m", "uvicorn", "pk_002.main:app", "--host", "0.0.0.0", "--port", "8000"]