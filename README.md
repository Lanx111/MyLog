# MyLog — 个人主页与成长日志系统

## 1. 项目简介

MyLog 是一个多用户全栈 Web 应用，支持：

- **展示个人信息**：姓名、职位、技术方向、学习目标、联系方式
- **记录成长日志**：工作日志、学习日志、日报、周报、阶段总结
- **多用户注册登录**：每人拥有独立的个人主页和日志空间
- **管理员系统**：管理员可查看和删除所有用户及日志
- **公开首页**：所有人可见所有成员的个人信息和近期日志

技术栈：**React + Vite（前端） + FastAPI + SQLite（后端） + Docker（部署）**

线上地址：**http://47.98.125.128**

---

## 2. 项目结构

```
MyLog/
├── README.md
├── docker-compose.yml              # Docker Compose 编排
├── start.sh / start.bat            # 本地一键启动脚本
│
├── backend/                        # Python FastAPI 后端
│   ├── requirements.txt            # Python 依赖
│   ├── main.py                     # 应用入口 + CORS
│   ├── database.py                 # SQLAlchemy 连接
│   ├── models.py                   # ORM 模型 (User, Profile, Post)
│   ├── schemas.py                  # Pydantic 请求/响应模型
│   ├── crud.py                     # 数据库 CRUD 操作
│   ├── auth_utils.py               # JWT 令牌 + 密码哈希
│   ├── dependencies.py             # FastAPI 依赖 (认证/管理员)
│   ├── init_db.py                  # 建表 + 种子数据
│   ├── entrypoint.sh               # Docker 启动脚本
│   ├── Dockerfile                  # 后端容器构建
│   └── routers/                    # API 路由
│       ├── auth.py                 # 注册 / 登录 / 当前用户
│       ├── profile.py              # 个人信息 (公开 + 认证)
│       ├── posts.py                # 日志 CRUD (公开 + 认证)
│       └── admin.py                # 管理员接口
│
└── frontend/                       # Vite + React 前端
    ├── index.html
    ├── vite.config.js              # Vite 配置 + API 代理
    ├── Dockerfile                  # 多阶段构建 (Node → Nginx)
    ├── nginx.conf                  # Nginx 静态服务 + 反向代理
    └── src/
        ├── main.jsx                # React 入口
        ├── App.jsx                 # 路由配置
        ├── api.js                  # API 请求封装 (支持 Token)
        ├── AuthContext.jsx          # 全局认证状态
        ├── ProtectedRoute.jsx       # 路由守卫
        ├── styles/
        │   └── global.css          # 全局样式 + CSS 变量
        ├── components/             # 可复用组件
        │   ├── Header.jsx          # 导航 (条件渲染)
        │   ├── PostCard.jsx        # 日志卡片 (带作者)
        │   ├── PostForm.jsx        # 日志表单
        │   └── ProfileCard.jsx     # 个人信息卡片
        └── pages/                  # 页面
            ├── HomePage.jsx        # 首页 (成员 + 日志标签)
            ├── PostListPage.jsx    # 日志列表 (筛选/搜索/分页)
            ├── PostDetailPage.jsx  # 日志详情
            ├── ProfileDetailPage.jsx  # 用户详情
            ├── AdminPage.jsx       # 个人管理 (资料 + 日志)
            ├── AdminDashboard.jsx  # 管理面板 (管理员用)
            ├── LoginPage.jsx       # 登录
            └── RegisterPage.jsx    # 注册
```

---

## 3. 技术选型与原因

| 层级 | 技术 | 选择理由 |
|------|------|----------|
| 前端框架 | **React 18** | 实习要求使用 |
| 构建工具 | **Vite** | React 官方推荐的现代构建工具，启动快、HMR 优秀 |
| 路由 | **React Router v6** | React 生态最主流的路由方案 |
| 样式 | **CSS Modules** | 零依赖，组件级样式隔离 |
| 后端框架 | **FastAPI** | 自动生成 Swagger 文档、Pydantic 类型验证、原生异步支持 |
| ORM | **SQLAlchemy 2.0** | Python 最成熟的 ORM |
| 数据库 | **SQLite** | 零配置、无需安装服务、单文件存储、方便备份迁移 |
| 密码哈希 | **hashlib (PBKDF2)** | Python 标准库，零外部依赖 |
| 身份令牌 | **JWT (python-jose)** | 无状态，前后端分离标准方案 |
| 部署 | **Docker + 阿里云** | 一键构建部署、环境隔离、易于扩展 |

### 为什么选择 Python 而不是 Go 或 Java？

对 Python 更为熟悉，可以更快完成交付。后续学习 Go 后考虑用 Go 重构后端。

### 为什么后端选择 FastAPI 而不是 Flask/Django？

1. **自动 API 文档**：`/docs` 直接提供 Swagger UI，调试方便
2. **类型安全**：Pydantic 自动验证请求/响应，减少运行时错误
3. **异步支持**：`async/await` 原生支持，未来扩展空间更大
4. **发展趋势**：FastAPI 是目前 Python Web 框架的增长最快选择

---

## 4. 数据模型与持久化方案

### 数据库：SQLite

- 零配置，无需安装数据库服务
- 单文件存储（`mylog.db`），复制文件即可备份
- Docker 部署时使用命名卷（`mylog_data`）挂载，容器重启数据不丢失
- 适合个人主页和日志系统这种并发量低的场景

### 数据模型

**users 表（用户账号）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| username | VARCHAR(50) UNIQUE | 用户名 |
| password_hash | VARCHAR(200) | PBKDF2 密码哈希 |
| is_admin | BOOLEAN | 是否管理员 |
| created_at | DATETIME | 注册时间 |

**profiles 表（个人信息，一个用户一条）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增 |
| user_id | INTEGER FK UNIQUE | 关联 users.id |
| name | VARCHAR(100) | 姓名 |
| title | VARCHAR(200) | 职位/角色 |
| avatar_url | TEXT | 头像链接 |
| bio | TEXT | 个人简介 |
| skills | TEXT (JSON) | 技能标签数组 |
| github_url | TEXT | GitHub |
| blog_url | TEXT | 博客 |
| email | VARCHAR(200) | 邮箱 |
| learning_goals | TEXT | 学习目标 |

**posts 表（日志）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增 |
| user_id | INTEGER FK | 作者 |
| title | VARCHAR(300) | 标题 |
| content | TEXT | 正文 |
| post_type | VARCHAR(20) | work_log / study_log / daily_report / weekly_report / summary |
| tags | TEXT (JSON) | 标签数组 |

### 数据流

```
浏览器 (React)
    ↕ fetch /api/*  (Authorization: Bearer <token>)
Nginx (前端容器 :80)
    ↕ proxy_pass
FastAPI (后端容器 :8000)
    ↕ SQLAlchemy ORM
SQLite (mylog.db，宿主机卷挂载)
```

所有数据通过 API 读写，核心内容不存储在 localStorage、sessionStorage 或前端 mock 数据中。JWT 令牌存储在 localStorage 中用于会话保持。

---

## 5. 我对需求的理解

这次实践的核心是：**构建一个导师能随时了解实习生进展的工具，而不仅仅是一个静态展示页。**

拆解为三个层次：
1. **"我是谁"** — 个人信息展示，访问者可快速了解技术背景和学习方向
2. **"我在做什么"** — 日志记录和查看，覆盖工作、学习、日报、周报等多种场景
3. **"怎么让导师看到"** — 服务端持久化 + 公网部署，换设备也能访问，多人可见

进一步扩展为多用户系统：每个实习生都有独立的空间，互相可见，导师可以查看所有人的进展。

### 核心约束

- React 前端 + Python 后端 + 服务端持久化 + 线上可访问
- 不能走捷径（如纯前端 localStorage 方案）

---

## 6. 核心用户流程

### 访客流程（未登录）

```
打开 http://47.98.125.128
    → 首页「成员」标签：看到所有用户的个人信息卡片
    → 点击用户卡片 → 用户详情页（完整资料 + 返回按钮）
    → 首页「日志」标签：看到所有用户的近期日志
    → 点击日志卡片 → 日志详情页（含作者信息）
    → 日志列表页：按类型筛选、关键词搜索、翻页
```

### 实习生流程（已登录）

```
注册/登录
    → 点击「我的」→ 编辑资料：姓名、技能、GitHub 等 → 保存
    → 写日志：选择类型、标题、内容、标签 → 发布
    → 日志列表中可编辑或删除已有日志
    → 首页可看到自己和所有人的内容
```

### 管理员流程

```
管理员登录 → 顶部出现「管理面板」
    → 「用户管理」标签：查看所有用户详情 → 删除用户（级联删除数据）
    → 「日志管理」标签：查看所有日志 → 删除任意日志
```

---

## 7. API 接口

### Auth（公开）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册（返回 JWT） |
| POST | `/api/auth/login` | 登录（返回 JWT） |
| GET | `/api/auth/me` | 当前用户信息（需 JWT） |

### Profile

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/profiles` | 公开 | 所有用户 profile |
| GET | `/api/profile` | JWT | 当前用户 profile |
| PUT | `/api/profile` | JWT | 更新当前用户 profile |

### Posts

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/posts` | 公开 | 日志列表（?type=&user_id=&page=&limit=&q=） |
| GET | `/api/posts/{id}` | 公开 | 日志详情 |
| POST | `/api/posts` | JWT | 创建日志 |
| PUT | `/api/posts/{id}` | JWT | 更新（仅作者） |
| DELETE | `/api/posts/{id}` | JWT | 删除（仅作者） |

### Admin（管理员）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/users` | 用户列表（含 profile 和日志数） |
| DELETE | `/api/admin/users/{id}` | 删除用户及所有数据 |
| DELETE | `/api/admin/posts/{id}` | 删除任意日志 |

---

## 8. 已完成功能

| 模块 | 功能 | 状态 |
|------|------|------|
| 个人主页 | 展示姓名、职位、头像、简介、技能、学习目标、联系方式 | ✅ |
| 多用户 | 注册、登录、JWT 认证、会话持久化 | ✅ |
| 权限隔离 | 只能管理自己的资料和日志 | ✅ |
| 管理员 | 查看/删除所有用户和日志 | ✅ |
| 用户详情 | 点击成员卡片查看完整信息 | ✅ |
| 日志列表 | 按类型筛选、关键词搜索、分页浏览 | ✅ |
| 日志详情 | 查看完整内容、作者信息、标签展示 | ✅ |
| 创建日志 | 工作日志、学习日志、日报、周报、总结 5 种类型 | ✅ |
| 编辑/删除日志 | 仅作者可操作 | ✅ |
| 编辑资料 | 网页表单修改个人信息 | ✅ |
| 首页标签 | 成员/日志标签切换，自适应网格布局 | ✅ |
| 服务端持久化 | SQLite 数据库，重启不丢数据 | ✅ |
| 响应式设计 | 桌面端和移动端均可正常使用 | ✅ |
| Swagger 文档 | `/docs` 自动生成 API 文档 | ✅ |
| Docker 部署 | docker-compose 一键构建部署 | ✅ |
| 公网访问 | http://47.98.125.128 | ✅ |

---

## 9. 未完成内容与后续计划

| 项目 | 优先级 | 说明 |
|------|--------|------|
| Markdown 支持 | 中 | 日志内容目前为纯文本，计划支持 Markdown 渲染 |
| 评论/反馈 | 中 | 导师可在日志下留言反馈 |
| 图片上传 | 低 | 日志中支持插入图片 |
| 数据备份 | 中 | 定时将 SQLite 备份到云端 |
| CI/CD | 低 | GitHub Actions 自动构建测试和部署 |
| HTTPS | 低 | 配置 SSL 证书，启用 HTTPS |
| 域名绑定 | 低 | 绑定自定义域名代替 IP 地址 |

---

## 10. 本地运行

### 环境要求

- Python >= 3.8（推荐 3.10+）
- Node.js >= 18
- npm >= 9

### 一键启动

```bash
# Windows（双击 start.bat 或在终端运行）
start.bat

# macOS / Linux / Git Bash
bash start.sh
```

### 手动启动

**启动后端**

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
python init_db.py               # 首次运行：建表 + 种子数据
uvicorn main:app --reload --port 8000
```

后端运行在 http://localhost:8000，API 文档在 http://localhost:8000/docs。

**启动前端**

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173。

### 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| `lanxin` | `123456` | 管理员 |
| `zhangsan` | `123456` | 普通用户 |

---

## 11. Docker 部署

```bash
# SSH 到服务器
ssh root@<服务器IP>
cd /root/MyLog

# 拉最新代码并重新构建
git pull
docker compose up -d --build

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f
```

注意：数据库文件通过 Docker 卷 `mylog_data` 持久化。切勿使用 `docker compose down -v`（`-v` 会删除数据卷）。

---

## 12. 线上访问地址

**http://47.98.125.128**

部署方式：Docker Compose on 阿里云 ECS

- 前端容器（Nginx + React）：80 端口对外
- 后端容器（FastAPI）：8000 端口（仅内部网络）
- 数据卷（SQLite）：宿主机持久化

---

## 13. AI 使用说明

本项目使用 **Claude Code**（CLI AI 编程助手）辅助开发。AI 参与了以下环节：

| 环节 | AI 参与内容 |
|------|------------|
| 架构设计 | 技术选型讨论、数据库表结构设计、API 接口设计、Docker 部署方案、多用户升级方案、管理员功能设计 |
| 代码生成 | 后端全部代码（FastAPI/SQLAlchemy CRUD、JWT 认证、权限隔离）+ 前端全部代码（React 组件、AuthContext、路由守卫） |
| 问题排查 | Python 版本兼容性、终端 GBK 编码、Windows venv 创建、passlib/bcrypt 兼容性（切换 PBKDF2）、FastAPI 422 验证错误处理、Docker 容器通信 |
| 文档编写 | 本 README 由 AI 辅助生成 |

所有 AI 生成的代码均经过本地运行验证和人工审查。

---

## License

MIT
