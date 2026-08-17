# AIMultiChat - 智能多Agent对话系统

基于 FastAPI 与 Ollama 构建的轻量级 Agent 调度框架，通过 Function Calling 与 ReAct 推理机制，实现复杂任务的多步自动拆解与跨系统执行。

## ✨ 核心特性

- **多Agent协同调度**：采用 Router-Executor-Aggregator 三层架构，支持意图识别、任务拆解与多工具协同调用
    
- **ReAct多步推理**：支持“查询天气 → 生成邮件”等复合指令的链式执行，单轮对话内完成多工具协同
    
- **SSE流式响应**：基于 FastAPI + asyncio 构建非阻塞 SSE 流式接口，提供实时“打字机”体验
    
- **RAG知识库增强**：集成检索增强生成能力，支持 PDF/Word/TXT 文档解析与向量检索，实现精准问答
    
- **完整的用户体系**：支持用户注册、登录、会话管理，多会话并发隔离
    
- **可观测性**：集成请求日志中间件与指标存储，支持按请求耗时与 Token 消耗进行性能调优
    

## 🛠️ 技术栈

- **后端框架**：FastAPI + Python 3.11+
    
- **异步驱动**：SQLAlchemy Async + asyncio
    
- **数据库**：MySQL + SQLite（指标存储）
    
- **向量数据库**：ChromaDB
    
- **大模型**：Ollama（本地量化部署）
    
- **Agent框架**：自研 ReAct + Function Calling
    
- **RAG链路**：文档解析 → 向量检索 → Cross-Encoder 重排序
    
- **容器化**：Docker + Docker Compose
    
- **前端**：原生 HTML/CSS/JavaScript + SSE
## 📁 项目结构

```
AIMultiChat/
├── docker/                 # Docker 相关配置
│   └── Dockerfile          # 多阶段构建镜像
├── frontend/               # 前端静态资源
│   ├── css/                # 样式文件
│   ├── js/                 # 前端逻辑（SSE 流式解析器）
│   └── index.html          # 主页面
├── src/                    # 后端源码
│   └── myproject/
│       ├── agents/         # Agent 核心模块
│       │   ├── registry.py # 工具注册中心
│       │   ├── superviser.py # Agent 监督与调度
│       │   ├── tools.py    # 工具定义（Function Calling）
│       │   └── woker.py    # 任务执行器
│       ├── services/       # 业务服务层
│       │   ├── auth.py     # 用户认证服务
│       │   ├── llm_service.py # 大模型调用服务
│       │   ├── rag_service.py # RAG 检索增强服务
│       │   ├── doc_processor.py # 文档解析处理
│       │   ├── message_service.py # 消息管理
│       │   ├── session_service.py # 会话管理
│       │   └── metrics_service.py # 性能指标采集
│       ├── models/         # 数据模型（SQLAlchemy）
│       ├── routers/        # API 路由
│       ├── middleware/     # 中间件（日志、鉴权）
│       ├── config.py       # 配置管理
│       ├── database.py     # 数据库连接
│       ├── deps.py         # 依赖注入
│       └── main.py         # 应用入口
├── alembic/                # 数据库迁移
├── .env.example            # 环境变量示例
└── docker-compose.yml      # 服务编排
```

## 🚀 快速开始

### 前置要求

- Python 3.11+
    
- Docker & Docker Compose（可选）
    
- MySQL 5.7+
    
- Ollama（本地大模型）
    

### 本地运行

1. **克隆仓库**
```
git clone https://github.com/czstars1/AIMultiChat.git
cd AIMultiChat
```
1. **配置环境变量**
```
cp .env.example .env
# 编辑 .env 文件，填写数据库连接等配置
```
2. **安装依赖**
```
pip install -r requirements.txt
```
3. **初始化数据库**
```
alembic upgrade head
```
4. **启动服务**
```
uvicorn src.myproject.main:app --host 0.0.0.0 --port 8000 --reload
```
4. **访问应用**  
```
打开浏览器访问 `http://localhost:8000`
```
### Docker 部署
```
docker-compose up -d
```
## 🔧 环境变量说明

|变量名|说明|示例|
|---|---|---|
|`DATABASE_URL`|MySQL 数据库连接串|`mysql+asyncmy://user:pass@localhost:3306/db`|
|`OLLAMA_BASE_URL`|Ollama 服务地址|`http://localhost:11434`|
|`DEFAULT_MODEL`|默认大模型|`qwen2.5:7b`|
|`CHROMA_PERSIST_DIR`|ChromaDB 持久化目录|`./chroma_data`|
|`SECRET_KEY`|JWT 签名密钥|`your-secret-key`|

## 📊 核心功能演示

### Agent 多步推理

用户输入“帮我查一下北京今天的天气，然后根据天气情况生成一封出行提醒邮件”，系统会：

1. Router 层识别意图并拆解为两个子任务
    
2. Executor 层依次调用天气查询工具和邮件生成工具
    
3. Aggregator 层聚合结果并返回给用户
    

### RAG 知识库问答

上传企业文档（PDF/Word/TXT）后，系统自动完成：

- 文档解析与切片（chunk_size=500, overlap=50）
    
- 向量化存储与索引构建
    
- 用户提问时检索 Top-K 相关片段
    
- Cross-Encoder 重排序精排，首条命中准确率达 92%
    

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
    
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
    
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
    
4. 推送到分支 (`git push origin feature/AmazingFeature`)
    
5. 开启一个 Pull Request
    

## 📝 待办事项

- [ ] 支持更多大模型提供商（OpenAI、通义千问等）

- [ ] 增加 Multi-Agent 协作模式（LangGraph/AutoGen 风格）

- [ ] 完善前端交互体验

- [ ] 增加更多内置工具（日历、邮件、计算器等）


## 📄 License

MIT License

---

**作者**：[chenzuqi](https://github.com/czstars1)

邮箱：chenzuqi2027@163.com
