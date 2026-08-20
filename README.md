# AI Agent Chat

> 基于 FastAPI + Ollama 的智能 Agent 对话系统：通过 Function Calling 与 ReAct 多步推理实现工具调度，内置 RAG 知识库问答与 SSE 流式对话，附带完整用户体系与现代响应式前端。

## ✨ 核心特性

- **Agent 工具调度**：基于 Ollama Function Calling 自动路由意图，统一管理天气、新闻、日期、RAG 检索、文书撰写等多类工具；支持单轮对话内多工具串联（如"查天气 → 生成邮件"），路由失败自动降级为普通聊天
- **SSE 流式对话**：基于 FastAPI + asyncio 构建非阻塞流式接口，采用类型化事件协议（content / sources / error / done），前端配合打字机光标与停止生成，提供实时"打字机"体验
- **RAG 知识库问答**：支持 PDF / Word / TXT 文档解析、切片与向量化入库，检索链路集成 Cross-Encoder 重排序，回答附带参考来源，可溯源、可核验
- **完整用户体系**：注册 / 登录、Bearer Token 鉴权、密码 PBKDF2 加盐哈希存储、多会话管理与越权隔离
- **现代响应式前端**：登录注册、会话搜索与管理、Markdown 渲染（防 XSS）、移动端抽屉式侧边栏
- **可观测性与工程化**：统一日志（控制台 + 滚动文件）、请求耗时中间件与性能指标落库、统一异常处理、Docker 一键部署

## 🛠️ 技术栈

| 层面 | 技术 |
|---|---|
| 后端框架 | FastAPI + Python 3.11+（uvicorn） |
| 数据访问 | SQLAlchemy 2.0（Async）+ MySQL（asyncmy 驱动） |
| 向量数据库 | ChromaDB |
| 大模型 | Ollama 本地推理（默认 `qwen2.5:7b`），流式 / 非流式调用 |
| Embedding / 重排序 | sentence-transformers（all-MiniLM-L6-v2）、CrossEncoder（ms-marco-MiniLM-L6-v2） |
| Agent 框架 | 自研：Function Calling + ReAct 多步推理 |
| 配置校验 | Pydantic v2 + pydantic-settings |
| 前端 | 原生 HTML / CSS / JavaScript（SSE 流式解析） |
| 部署 | Docker / Docker Compose |

## 📁 项目结构

```
ai-agent-chat/
├── frontend/                 # 前端静态资源
│   ├── css/style.css         # 样式
│   ├── js/                   # config / state / api / ui / main
│   └── index.html            # 主页面
├── src/myproject/
│   ├── agents/               # Agent 核心
│   │   ├── supervisor.py     # 路由调度与多步执行
│   │   ├── worker.py         # 文书撰写执行器
│   │   └── tools.py          # 工具实现与注册表
│   ├── services/             # 业务服务层
│   │   ├── llm_service.py    # LLM 调用（重试 / 超时 / 流式）
│   │   ├── rag_service.py    # RAG 检索增强服务
│   │   ├── doc_processor.py  # 文档解析与向量化
│   │   ├── vector_store.py   # ChromaDB 与模型加载
│   │   ├── stream_events.py  # SSE 事件协议
│   │   ├── auth.py           # 认证（PBKDF2 哈希）
│   │   ├── session_service.py / message_service.py / metrics_service.py
│   ├── models/               # Pydantic 请求/响应 + ORM 模型
│   ├── routers/              # auth / sessions / chat / rag / agent
│   ├── dependencies/         # 鉴权与数据库会话依赖
│   ├── middleware/timing.py  # 请求耗时统计中间件
│   ├── config.py             # 集中配置（pydantic-settings）
│   ├── database.py           # 异步引擎与会话
│   ├── logging_config.py     # 日志配置
│   └── main.py               # 应用入口（lifespan 管理）
├── models/                   # 本地 Embedding / 重排序模型
├── data/                     # ChromaDB 持久化与上传文档
├── tests/                    # pytest 单元测试
├── alembic/                  # 数据库迁移（可选）
├── docker/Dockerfile         # 容器化部署镜像
├── docker-compose.yml        # MySQL + 应用编排
└── .env.example              # 环境变量示例
```

## 🚀 快速开始

### 前置要求

- Python 3.11+
- MySQL 5.7+（本地或 Docker）
- Ollama（本地大模型，需先 `ollama pull qwen2.5:7b`）
- RAG 功能依赖本地模型目录 `models/`（Embedding 与重排序模型）

### 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/czstars1/ai-agent-chat.git  
cd ai-agent-chat

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填写数据库连接与模型配置

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务（启动时自动建表，无需手动初始化数据库）
uvicorn src.myproject.main:app --host 0.0.0.0 --port 8000 --reload
# 或 python -m src.myproject.main
```

打开浏览器访问 `http://localhost:8000`，注册账号后即可开始对话。

### Docker 部署

```bash
docker-compose up -d
```

## 🔧 环境变量说明

| 变量名 | 说明 | 示例 |
|---|---|---|
| `DATABASE_URL` | MySQL 连接串（asyncmy 驱动） | `mysql+asyncmy://root:123456@localhost:3306/ai_chat_app` |
| `OLLAMA_URL` | Ollama Chat API 地址 | `http://localhost:11434/api/chat` |
| `MODEL_NAME` | 使用的模型名称 | `qwen2.5:7b` |
| `DEBUG` | 调试模式（热重载 / 详细日志） | `True` / `False` |
| `PORT` | 服务端口 | `8000` |

## 📡 API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/auth/register` | 用户注册 |
| POST | `/auth/login` | 用户登录 |
| GET / POST | `/sessions` | 会话列表 / 创建会话 |
| PUT / DELETE | `/sessions/{id}` | 重命名 / 删除会话 |
| POST | `/chat/` | 非流式对话 |
| POST | `/chat/stream` | 流式对话（SSE） |
| GET | `/chat/{id}/messages` | 会话历史消息 |
| POST | `/agent/chat` | Agent 对话（工具调度 + 流式 SSE） |
| POST | `/rag/upload` | 上传文档建立索引 |
| GET | `/rag/docs` | 知识库文档列表 |
| POST | `/rag/ask` | 知识库问答（非流式） |
| POST | `/rag/ask/stream` | 知识库问答（SSE 流式） |
| GET | `/api/health` | 健康检查 |

## 💡 使用示例

### Agent 多步工具调用

输入「帮我查一下北京今天的天气，然后根据天气情况生成一封出行提醒邮件」，系统会：

1. 路由层识别意图并拆解任务
2. 依次调用天气查询工具与文书撰写工具
3. 流式返回最终成文，并在对话中保存完整记录

### RAG 知识库问答

1. 点击「上传文档」，上传 PDF / Word / TXT
2. 系统自动完成解析、切片（chunk_size=500, overlap=50）、向量化入库
3. 提问时检索 Top-K 候选 → Cross-Encoder 重排序精排 → LLM 基于资料生成回答
4. 回答附带参考来源，支持人工核验

## 📝 待办事项

- [ ] 支持更多模型提供商（OpenAI、通义千问等）与多模型 Fallback
- [ ] 增加 Multi-Agent 协作模式（LangGraph / AutoGen 风格）
- [ ] 增加更多内置工具（日历、邮件、计算器等）
- [ ] 完善对话历史的分页加载与全文检索

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/xxx`）
3. 提交改动（`git commit -m 'feat: xxx'`）
4. 推送到分支并开启 Pull Request

---

**作者**：[chenzuqi](https://github.com/czstars1)　邮箱：chenzuqi2027@163.com
