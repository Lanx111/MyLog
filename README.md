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
| 前端框架 | **React ** | 极致的灵活性、庞大的生态和社区、跨平台能力 |
| 构建工具 | **Vite** | React 官方推荐的现代构建工具，相比 CRA 启动更快、HMR 更优 |
| 路由 | **React Router v6** | React 生态最主流的路由方案 |
| 后端框架 | **FastAPI** | 现代 Python Web 框架，自动生成 Swagger API 文档，原生异步支持，Pydantic 数据验证开箱即用 |
| ORM | **SQLAlchemy 2.0** | Python 生态最成熟的 ORM，与 FastAPI 配合良好 |
| 数据库 | **SQLite** | 零配置的嵌入式数据库，本地开发无需安装任何数据库服务，部署简单；数据以文件形式存储，方便备份和迁移 |

### 为什么选择python而不是go或者java等？

对python更为熟悉，后面了解go后会考虑用go来实现后端部分。

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

### 一键启动

```bash
# Windows（双击 start.bat 或在终端运行）
start.bat
# macOS / Linux / Git Bash
bash start.sh
```

## 线上部署

> 部署说明：Docker+阿里云

**部署地址：** _http://47.98.125.128_

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
