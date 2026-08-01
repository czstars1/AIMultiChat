import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
print("HF_ENDPOINT:", os.environ.get("HF_ENDPOINT"))
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from src.myproject.config import BASE_DIR,PORT
from src.myproject.routers import rag,sessions, chat,auth
from src.myproject.middleware.timing import add_process_time_header
from src.myproject.database import init_db

# ----- 1. 将 app 定义为全局变量（模块级别）-----
frontend_path = BASE_DIR / "frontend"

app = FastAPI(
    title="我的聊天API",
)
init_db()
# CORS 配置
origins = ["http://localhost:63342"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(rag.router)

# 自定义中间件
@app.middleware("http")
async def add_process_time_header1(request: Request, call_next):
    return await add_process_time_header(request, call_next)

# 挂载静态文件
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# ----- 2. 保留 main() 函数用于直接运行 -----
def main():
    # 直接运行全局的 app
    uvicorn.run(app, host="127.0.0.1", port=PORT)

if __name__ == "__main__":
    main()