from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from pk_002.middleware.timing import add_process_time_header

from pk_002.routers import sessions, chat,auth
from pk_002.database import init_db
from pk_002.models import db_models  # 导入以确保模型注册到 Base

# ----- 1. 将 app 定义为全局变量（模块级别）-----
BASE_DIR = Path(__file__).resolve().parent
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

# 自定义中间件
@app.middleware("http")
async def add_process_time_header1(request: Request, call_next):
    return await add_process_time_header(request, call_next)

# 挂载静态文件
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


# ----- 2. 保留 main() 函数用于直接运行 -----
def main():
    # print("初始化数据库...")
    # init_db()
    # print("数据库初始化完成。")

    # 直接运行全局的 app
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()