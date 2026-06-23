# CLAUDE.md — MyLog 项目开发指南

## 项目概述

MyLog 是一个多用户全栈 Web 应用，用于展示个人信息和记录成长日志（工作日志、学习日志、日报、周报、总结）。支持全站访问码保护、JWT 登录认证、权限隔离和管理员功能。

- **线上地址**: http://47.98.125.128
- **仓库**: https://github.com/Lanx111/MyLog
- **主要语言**: 中文（代码注释、UI、文档均为中文）

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | React + Vite + React Router | React 19, Vite 8, Router v7 |
| 样式 | CSS Modules + CSS Variables | — |
| 后端 | FastAPI + SQLAlchemy | FastAPI 0.136, SQLAlchemy 2.0 |
| 数据库 | SQLite | 单文件存储 |
| 认证 | JWT (python-jose) + PBKDF2 密码哈希 | — |
| AI Agent | DeepSeek API + httpx | — |
| 部署 | Docker + Docker Compose + Nginx | — |

## 项目结构

```
MyLog/
├── backend/          # Python FastAPI 后端
│   ├── main.py       # 应用入口 + CORS + 访问码中间件
│   ├── database.py   # SQLAlchemy 引擎和会话
│   ├── models.py     # ORM 模型 (User, Profile, Post)
│   ├── schemas.py    # Pydantic 请求/响应模型
│   ├── crud.py       # 数据库 CRUD 操作
│   ├── auth_utils.py # JWT + 密码哈希 + 访问码
│   ├── dependencies.py # FastAPI 依赖注入 (认证/管理员)
│   ├── init_db.py    # 建表 + 种子数据
│   ├── routers/      # API 路由 (auth, profile, posts, admin)
│   └── tests/        # pytest 测试
├── frontend/         # Vite + React 前端
│   └── src/
│       ├── App.jsx          # 路由配置
│       ├── api.js           # fetch 封装 (Token + Access-Token)
│       ├── AuthContext.jsx   # 全局认证状态
│       ├── ProtectedRoute.jsx # 路由守卫
│       ├── components/      # 可复用组件 (Header, AccessGate, PostCard, PostForm, ProfileCard)
│       └── pages/           # 页面组件 (Home, PostList, PostDetail, Admin, Login 等)
├── agent/            # 日报 AI Agent (DeepSeek)
│   └── daily_report.py
├── docker-compose.yml
└── start.sh / start.bat  # 本地一键启动脚本
```

## 常用命令

### 后端

```bash
cd backend
# 激活虚拟环境
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate.bat       # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（首次运行：建表 + 种子数据）
python init_db.py

# 启动开发服务器（热重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
python -m pytest tests/

# 运行单个测试文件
python -m pytest tests/test_auth.py

# 运行单个测试
python -m pytest tests/test_auth.py::TestAuth::test_login_with_correct_credentials
```

后端运行在 http://localhost:8000，API 文档在 http://localhost:8000/docs。

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（热重载，端口 5173，自动代理 /api → localhost:8000）
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview

# ESLint 检查
npm run lint

# 运行测试
npm test
# 即 vitest run

# 监听模式运行测试
npm run test:watch
# 即 vitest

# 运行单个测试文件
npx vitest run src/test/components.test.jsx
```

前端运行在 http://localhost:5173。Vite 配置了 `/api` 代理到 `http://localhost:8000`。

### Docker 部署

```bash
# 构建并启动
docker compose up -d --build

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止（注意：不要加 -v，会删除数据卷）
docker compose down
```

### 一键本地启动

```bash
bash start.sh       # Linux/Mac
start.bat           # Windows（双击或命令行）
```

## 环境变量

### 后端 (`backend/.env`)

| 变量 | 必须 | 说明 | 默认值 |
|------|------|------|--------|
| `JWT_SECRET` | ✅ | JWT 签名密钥 | 无（启动时会报错） |
| `CORS_ORIGINS` | ❌ | CORS 允许的来源，逗号分隔 | `http://localhost:5173,http://localhost:3000` |
| `DATABASE_URL` | ❌ | 数据库连接 | `sqlite:///./mylog.db` |
| `ACCESS_CODE` | ❌ | 全站访问码 | `mylog2026` |

### Agent (`agent/.env`)

`DEEPSEEK_KEY`, `DEEPSEEK_BASE`, `MYLOG_URL`, `MYLOG_USER`, `MYLOG_PASS`, `NOTES_DIR`, `WEBHOOK_URL` — 详见 `agent/.env.example`。

## 架构概览

### 后端架构 (FastAPI)

- **入口**: `main.py` — 创建 FastAPI app，注册中间件和路由
- **中间件**:
  - `access_gate`: 所有 `/api/` 请求需携带 JWT 或 `X-Access-Token`（白名单路径除外）
  - `log_requests`: 请求日志记录
- **路由** (`routers/`): 按功能域拆分 — `auth.py`, `profile.py`, `posts.py`, `admin.py`
- **依赖注入** (`dependencies.py`): `get_current_user` (JWT), `get_optional_user`, `get_admin_user`
- **ORM 模型** (`models.py`): `User`, `Profile` (一对一), `Post` (一对多)
- **CRUD** (`crud.py`): 所有数据库操作集中在此
- **响应格式**: 统一使用 `ApiResponse(code, message, data)` 包装

### 前端架构 (React)

- **路由**: React Router v7，在 `App.jsx` 中配置
- **认证**: `AuthContext` 提供全局认证状态，JWT 存储在 localStorage
- **访问控制**:
  - `AccessGate` 组件: 访客需通过访问码验证（token 存储在 sessionStorage）
  - `ProtectedRoute`: 需要登录
  - `AdminRoute`: 需要登录 + 管理员权限
- **样式**: CSS Modules (组件级) + `global.css` (CSS Variables 主题)
- **API 封装**: `api.js` 统一处理 fetch、Token 注入、错误处理

### 数据流

```
浏览器 (React :5173)
  ↕ fetch /api/* (Authorization: Bearer <JWT> / X-Access-Token)
Vite 代理 (开发) / Nginx 反向代理 (生产 :80)
  ↕ proxy_pass
FastAPI (:8000)
  ↕ 访问码中间件 → JWT / Access-Token 校验
  ↕ SQLAlchemy ORM
SQLite (data/mylog.db)
```

## 测试

### 后端测试 (pytest)

- **框架**: pytest + FastAPI TestClient
- **数据库**: 使用内存 SQLite (`sqlite:///:memory:`) + `StaticPool`，每个测试独立的表，无需文件系统上的 .db 文件
- **位置**: `backend/tests/`
- **约定**: 测试类按功能分组 (TestAuth, TestPosts, TestAdmin)，fixture 在 `conftest.py`

**关键 fixture**（`conftest.py`）：

| fixture | 作用 |
|---------|------|
| `client` | 注入测试数据库的 `TestClient`，通过 `app.dependency_overrides[get_db]` 替换会话 |
| `auth` | 注册一个普通测试用户，返回 `(headers_dict, user_dict)` |
| `admin` | 注册测试用户后手动提升为管理员（`is_admin=True`），返回 `(headers_dict, user_dict)` |
| `setup_db` | `autouse=True`，每个测试前建表、测试后删表，保证测试隔离 |

- **注意**: 测试中使用了 `/api/auth/register` 端点（该端点在生产中已关闭，仅在测试 fixture 中通过 `client` 直接调用以创建测试用户）

### 前端测试 (vitest)

- **框架**: vitest + @testing-library/react + @testing-library/jest-dom + jsdom
- **位置**: `frontend/src/test/`
- **配置**: `vite.config.js` 中的 `test` 字段
- **setup**: `src/test/setup.js`（导入 `@testing-library/jest-dom`）
- **约定**: 使用 `MemoryRouter` 包裹需要路由的组件，中文测试描述

## 代码风格与约定

- **语言**: 所有代码注释、提交信息、文档、UI 文本均为**中文**
- **后端**:
  - 纯 Python（非 TypeScript），无类型注解强制要求
  - 模块级 docstring 描述文件用途
  - 函数命名: `snake_case`
  - Pydantic schema 用于请求/响应验证
  - 所有 API 响应统一使用 `ApiResponse` 包装
- **前端**:
  - JavaScript (JSX)，非 TypeScript
  - 函数组件 + Hooks (useState, useEffect, useCallback, useRef)
  - 组件文件: `PascalCase.jsx`
  - CSS Module 文件: `PascalCase.module.css`
  - 导出方式: `export default function ComponentName()`
- **Git**:
  - 分支: 仅 `main`
  - 提交信息格式: `feat:`, `chore:`, `docs:` 等 conventional commits（中文描述）
  - 示例: `feat: v2 多用户系统 + 管理员功能 + 工程能力`

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| `lanxin` | `Lanxin@2026` | 管理员 |
| `zhangsan` | `Zhangsan@2026` | 普通用户 |

本地开发时访问码为 `mylog2026`，打开 `http://localhost:5173?code=mylog2026` 可直接进入。

## 重要注意事项

- `.env` 文件已在 `.gitignore` 中，不会被提交。首次运行需手动创建（项目中没有 `.env.example` 模板，需自行创建）。
- Docker 部署时**不要**使用 `docker compose down -v`，会删除数据库卷。
- 注册接口已在生产环境关闭，新用户需由管理员创建。
- `auth_utils.py` 在导入时即检查 `JWT_SECRET`，未设置会直接抛出 `RuntimeError`。
- `database.py` 和 `auth_utils.py` **各自独立调用** `load_dotenv` 加载 `.env`，因此从任意模块导入都会触发 JWT_SECRET 检查。`.env` 文件需放在 `backend/` 目录下。
- 前端 CSS 使用 CSS Variables 定义主题色（见 `global.css` 的 `:root`），修改主题色只需改变量。
