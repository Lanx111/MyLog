# MyLog — 个人主页与成长日志系统

一个基于 **React + FastAPI + SQLite** 的全栈个人主页与成长日志系统。

## 项目简介

MyLog 用于展示个人信息、技术方向和学习目标，同时支持记录和查看工作日志、学习日志、日报和阶段总结。导师或团队负责人可以通过这个系统快速了解近期进展、问题和计划。

### 核心功能

- **个人主页** — 展示姓名、职位、技能、学习目标、联系方式等
- **日志系统** — 支持工作日志、学习日志、日报、总结四种类型
- **分类筛选** — 按类型筛选、关键词搜索、分页浏览
- **管理后台** — 编辑个人资料、创建/编辑/删除日志
- **服务端持久化** — 所有数据存储在服务端 SQLite 数据库，换设备也能访问
- **响应式设计** — 支持桌面和移动端访问

## 技术选型

| 层级 | 技术 | 选择理由 |
|------|------|----------|
| 前端框架 | **React 18** | 任务要求使用 React |
| 构建工具 | **Vite** | React 官方推荐的现代构建工具，相比 CRA 启动更快、HMR 更优 |
| 路由 | **React Router v6** | React 生态最主流的路由方案 |
| 样式 | **CSS Modules** | 零依赖，组件级样式隔离，学习成本低 |
| 后端框架 | **FastAPI** | 现代 Python Web 框架，自动生成 Swagger API 文档，原生异步支持，Pydantic 数据验证开箱即用 |
| ORM | **SQLAlchemy 2.0** | Python 生态最成熟的 ORM，与 FastAPI 配合良好 |
| 数据库 | **SQLite** | 零配置的嵌入式数据库，本地开发无需安装任何数据库服务，部署简单；数据以文件形式存储，方便备份和迁移 |

### 为什么后端选择 FastAPI 而不是 Flask/Django？

1. **自动 API 文档**：FastAPI 自动生成 Swagger UI（`/docs`），开发调试更方便
2. **类型安全**：基于 Pydantic 的请求/响应验证，减少运行时错误
3. **异步原生**：支持 `async/await`，未来扩展性能空间更大
4. **学习价值**：FastAPI 是当前 Python 后端的发展趋势，学习它更有长期价值

## 项目结构

```
MyLog/
├── README.md
├── backend/
│   ├── requirements.txt      # Python 依赖
│   ├── main.py               # FastAPI 入口 + CORS 配置
│   ├── database.py           # SQLAlchemy 数据库连接
│   ├── models.py             # ORM 数据模型 (Profile, Post)
│   ├── schemas.py            # Pydantic 请求/响应模型
│   ├── crud.py               # 数据库增删改查操作
│   ├── init_db.py            # 数据库初始化 + 种子数据
│   └── routers/
│       ├── profile.py        # GET/PUT /api/profile
│       └── posts.py          # CRUD /api/posts
└── frontend/
    ├── index.html
    ├── vite.config.js         # Vite 配置 + API 代理
    └── src/
        ├── main.jsx           # React 入口
        ├── App.jsx            # 路由配置
        ├── api.js             # API 请求封装
        ├── styles/
        │   └── global.css     # 全局样式
        ├── pages/
        │   ├── HomePage.jsx   # 首页：个人信息 + 近期日志
        │   ├── PostListPage.jsx    # 日志列表：筛选 + 搜索 + 分页
        │   ├── PostDetailPage.jsx  # 日志详情
        │   └── AdminPage.jsx      # 管理页：编辑资料 + 管理日志
        └── components/
            ├── Header.jsx     # 顶部导航
            ├── ProfileCard.jsx    # 个人信息卡片
            ├── PostCard.jsx       # 日志卡片
            └── PostForm.jsx       # 日志创建/编辑表单
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/profile` | 获取个人信息 |
| PUT | `/api/profile` | 更新个人信息 |
| GET | `/api/posts` | 日志列表（支持 `?type=&page=&limit=&q=`） |
| POST | `/api/posts` | 创建日志 |
| GET | `/api/posts/{id}` | 获取单条日志 |
| PUT | `/api/posts/{id}` | 更新日志 |
| DELETE | `/api/posts/{id}` | 删除日志 |

启动后端后可访问 http://localhost:8000/docs 查看 Swagger API 文档。

## 本地运行

### 环境要求

- **Python** >= 3.8（推荐 3.10+）
- **Node.js** >= 18（推荐 20+）
- **npm** >= 9

### 一键启动（推荐）

```bash
# Windows（双击 start.bat 或在终端运行）
start.bat

# macOS / Linux / Git Bash
bash start.sh
```

两个脚本会自动启动后端（8000 端口）和前端（5173 端口），然后打开浏览器访问 http://localhost:5173 即可。

### 手动启动

#### 1. 启动后端

```bash
cd backend

# 创建虚拟环境（首次）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（首次运行，生成种子数据）
python init_db.py

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端运行在 http://localhost:8000，API 文档在 http://localhost:8000/docs。

### 2. 启动前端

```bash
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

前端运行在 http://localhost:5173，已配置代理将 `/api` 请求转发到后端。

### 3. 访问

打开浏览器访问 http://localhost:5173 即可使用系统。

## 验证方法

### 验证数据持久化

1. 访问首页 → 看到个人信息和种子日志
2. 进入「管理」页 → 点击「写日志」→ 填写并发布一条日志
3. 返回「首页」→ 确认新日志出现在「近期日志」中
4. 刷新页面（F5）→ 确认数据仍然存在
5. 停止并重启后端服务 → 确认数据没有丢失

### 验证跨设备访问

1. 在电脑 A 上启动前后端服务
2. 在电脑 A 的管理页创建一条日志
3. 用手机或另一台电脑访问电脑 A 的前端地址（确保在同一网络）
4. 确认能看到相同的日志内容

### 验证 API

```bash
# 获取个人信息
curl http://localhost:8000/api/profile

# 获取日志列表
curl http://localhost:8000/api/posts

# 按类型筛选
curl "http://localhost:8000/api/posts?post_type=work_log"

# 搜索
curl "http://localhost:8000/api/posts?q=React"

# 创建日志
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"测试","content":"内容","post_type":"work_log","tags":["test"]}'
```

## 线上部署

> 部署说明：如需部署到公网，建议：

- **前端**：部署到 [Vercel](https://vercel.com) 或 [Netlify](https://netlify.com)（免费）
- **后端**：部署到 [Render](https://render.com) 或 [Railway](https://railway.app)（免费）

部署时需将前端 `vite.config.js` 中的代理配置替换为实际后端 URL（设置环境变量 `VITE_API_BASE`）。

**部署地址：** _（待补充）_

## AI 参与方式说明

本项目使用 Claude Code（CLI AI 编程助手）辅助开发，AI 参与的范围包括：

1. **架构设计**：根据需求文档，AI 参与了技术选型讨论、数据库表结构设计、API 接口设计
2. **代码生成**：AI 生成了大部分后端（FastAPI/SQLAlchemy）和前端（React/Vite）代码
3. **调试修复**：AI 协助解决了 Python 版本兼容性、终端编码、venv 创建等问题
4. **文档编写**：本 README 由 AI 辅助生成

所有 AI 生成的代码均经过人工审查、本地运行验证。开发过程中遇到的每个技术决策和问题修复，开发者都需要理解其原理并能够解释。

人类开发者的工作重点是：需求分析、产品设计、方案验证、代码审查和功能测试。

## License

MIT
