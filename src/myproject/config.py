from pathlib import Path
import os
from dotenv import load_dotenv

# 1. 定义项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 2. 加载 .env 文件（只加载一次，全局生效）
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
    print(f"✅ 已加载环境变量: {env_file}")
else:
    print(f"⚠️ 未找到 .env 文件，将使用系统环境变量")

# 3. 定义常用路径
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "knowledge_docs"

# 4. 定义配置常量（从环境变量读取，带默认值）
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:root1234@localhost:3306/ai_chat_app"
)

OLLAMA_CHAT_API = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/chat"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "qwen2.5:7b"
)
# 5. 其他可选的配置项
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
PORT = int(os.getenv("PORT", 8000))