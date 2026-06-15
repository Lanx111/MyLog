# MyLog — 个人主页与成长日志系统

## 1. 项目简介

MyLog 是一个多用户全栈 Web 应用，支持：

- **展示个人信息**：姓名、职位、技术方向、学习目标、联系方式
- **记录成长日志**：工作日志、学习日志、日报、周报、阶段总结
- **全站访问码保护**：访客需通过分享链接（`?code=xxx`）或输入访问码才能浏览内容
- **登录写作**：已登录用户可创建、编辑、删除自己的日志和个人资料
- **管理员系统**：管理员可查看和删除所有用户及日志
- **草稿自动保存**：编辑日志时自动保存草稿，意外关闭可恢复

技术栈：**React + Vite（前端） + FastAPI + SQLite（后端） + Docker（部署）**

线上地址：**http://47.98.125.128**

---

## 2. 访问控制机制

### 访客（未登录）

```
分享链接: http://47.98.125.128?code=mylog2026
                ↓
        自动验证访问码 → 进入首页
                ↓
        浏览成员信息、日志列表、日志详情、个人主页 ✅
        写日志 / 编辑资料 ❌（需登录）
```

- 直接访问 `http://47.98.125.128`（无 `?code=`）→ 显示访问码输入页
- 访问码验证后，**本次浏览器会话内**无需重复输入
- **注册入口已关闭**，新用户需由管理员创建

### 已登录用户

- 登录后自动跳过访问码检查
- 可进入「我的」页面写日志、编辑个人资料
- 只能编辑和删除自己的内容

### 管理员

- 顶部出现「管理面板」入口
- 可查看所有用户详情、删除用户（级联删除其所有数据）
- 可删除任意日志

---

## 3. 项目结构

```
MyLog/
├── README.md
├── docker-compose.yml              # Docker Compose 编排
├── start.sh / start.bat            # 本地一键启动脚本
│
├── backend/                        # Python FastAPI 后端
│   ├── .env                        # 环境变量（JWT_SECRET、ACCESS_CODE 等）
│   ├── requirements.txt            # Python 依赖
│   ├── main.py                     # 应用入口 + CORS + 访问码中间件
│   ├── database.py                 # SQLAlchemy 连接 + .env 加载
│   ├── models.py                   # ORM 模型 (User, Profile, Post)
│   ├── schemas.py                  # Pydantic 请求/响应模型
│   ├── crud.py                     # 数据库 CRUD 操作
│   ├── auth_utils.py               # JWT 令牌 + 密码哈希 + 访问码验证
│   ├── dependencies.py             # FastAPI 依赖 (认证/管理员)
│   ├── init_db.py                  # 建表 + 种子数据
│   ├── entrypoint.sh               # Docker 启动脚本
│   ├── Dockerfile                  # 后端容器构建
│   └── routers/                    # API 路由
│       ├── auth.py                 # 访问码验证 / 登录 / 当前用户
│       ├── profile.py              # 个人信息 (浏览 + 认证)
│       ├── posts.py                # 日志 CRUD (浏览 + 认证)
│       └── admin.py                # 管理员接口
│
├── agent/                          # 日报 Agent（AI 自动生成日报）
│   ├── .env                        # Agent 配置（DeepSeek API 等）
│   ├── .env.example                # 配置模板（不含真实凭据）
│   ├── daily_report.py             # Agent 主脚本
│   └── requirements.txt
│
└── frontend/                       # Vite + React 前端
    ├── index.html
    ├── vite.config.js              # Vite 配置 + API 代理
    ├── Dockerfile                  # 多阶段构建 (Node → Nginx)
    ├── nginx.conf                  # Nginx 静态服务 + 反向代理
    └── src/
        ├── main.jsx                # React 入口
        ├── App.jsx                 # 路由配置
        ├── api.js                  # API 请求封装 (Token + Access-Token)
        ├── AuthContext.jsx          # 全局认证状态
        ├── ProtectedRoute.jsx       # 路由守卫 (登录 + 管理员)
        ├── components/             # 可复用组件
        │   ├── Header.jsx          # 导航栏 (条件渲染)
        │   ├── AccessGate.jsx      # 🔐 全站访问码门控
        │   ├── PostCard.jsx        # 日志卡片 (带作者)
        │   ├── PostForm.jsx        # 日志表单 (含草稿自动保存)
        │   └── ProfileCard.jsx     # 个人信息卡片
        └── pages/                  # 页面
            ├── HomePage.jsx        # 首页 (成员 + 日志标签)
            ├── PostListPage.jsx    # 日志列表 (筛选/搜索/分页)
            ├── PostDetailPage.jsx  # 日志详情
            ├── ProfileDetailPage.jsx  # 用户详情
            ├── AdminPage.jsx       # 个人管理 (资料 + 日志)
            ├── AdminDashboard.jsx  # 管理面板 (管理员用)
            ├── LoginPage.jsx       # 登录
            └── RegisterPage.jsx    # 注册（已隐藏入口）
```

---

## 4. 技术选型与原因

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

## 5. 数据模型与持久化方案

### 数据库：SQLite

- 零配置，无需安装数据库服务
- 单文件存储（`data/mylog.db`），复制文件即可备份
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
    ↕ fetch /api/*  (Authorization: Bearer <JWT> / X-Access-Token: <token>)
Nginx (前端容器 :80)
    ↕ proxy_pass
FastAPI (后端容器 :8000)
    ↕ 访问码中间件 → 校验 JWT 或 X-Access-Token
    ↕ SQLAlchemy ORM
SQLite (data/mylog.db，宿主机卷挂载)
```

所有数据通过 API 读写，核心内容不存储在 localStorage、sessionStorage 或前端 mock 数据中。JWT 令牌存储在 localStorage 中用于会话保持，访问码 token 存储在 sessionStorage 中。

---

## 6. 安全措施

| 措施 | 说明 |
|------|------|
| 全站访问码 | 访客必须通过访问码验证才能浏览内容，访问码不暴露在前端代码中 |
| JWT 认证 | 写操作（创建/编辑/删除）必须携带有效 JWT |
| 密码强度 | 最低 8 位密码，PBKDF2 + SHA256 + 随机 Salt 哈希存储 |
| CORS 限制 | 通过 `CORS_ORIGINS` 环境变量精确配置允许的前端来源 |
| JWT 密钥强制 | 启动时必须设置 `JWT_SECRET` 环境变量，否则拒绝启动 |
| 管理员权限 | 前端 AdminRoute + 后端 `get_admin_user` 双重校验 |
| 注册已关闭 | 前端隐藏注册入口 + 后端移除注册接口 |
| 时序攻击防护 | 密码比对使用 `secrets.compare_digest` |
| 敏感信息保护 | `.env` 文件已在 `.gitignore` 中，`.env.example` 只含占位符 |

---

## 7. API 接口

> 所有 `/api/` 接口（白名单除外）需携带 `X-Access-Token` 或 `Authorization: Bearer <JWT>` 请求头。

### Auth

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/auth/access` | 无 | 验证访问码，返回 access_token |
| POST | `/api/auth/login` | 无 | 登录，返回 JWT |
| GET | `/api/auth/me` | JWT | 当前登录用户信息 |

### Profile

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/profiles` | 访问码 | 所有用户 profile |
| GET | `/api/profile` | JWT | 当前用户 profile |
| PUT | `/api/profile` | JWT | 更新当前用户 profile |

### Posts

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/posts` | 访问码 | 日志列表（?post_type=&user_id=&page=&limit=&q=） |
| GET | `/api/posts/{id}` | 访问码 | 日志详情 |
| POST | `/api/posts` | JWT | 创建日志 |
| PUT | `/api/posts/{id}` | JWT | 更新日志（仅作者） |
| DELETE | `/api/posts/{id}` | JWT | 删除日志（仅作者） |

### Admin（管理员）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/users` | 用户列表（含 profile 和日志数） |
| DELETE | `/api/admin/users/{id}` | 删除用户及所有数据 |
| DELETE | `/api/admin/posts/{id}` | 删除任意日志 |

---

## 8. 环境变量

### 后端（`backend/.env`）

| 变量 | 必须 | 说明 | 示例 |
|------|------|------|------|
| `JWT_SECRET` | ✅ | JWT 签名密钥 | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `CORS_ORIGINS` | ❌ | CORS 允许的来源，逗号分隔 | `http://localhost:5173,https://mylog.com` |
| `DATABASE_URL` | ❌ | 数据库连接（默认 SQLite） | `sqlite:///./data/mylog.db` |
| `ACCESS_CODE` | ❌ | 全站访问码 | `mylog2026` |

### Agent（`agent/.env`）

| 变量 | 说明 |
|------|------|
| `DEEPSEEK_KEY` | DeepSeek API Key |
| `DEEPSEEK_BASE` | DeepSeek API 地址 |
| `MYLOG_URL` | MyLog 服务器地址 |
| `MYLOG_USER` / `MYLOG_PASS` | MyLog 账号密码 |
| `NOTES_DIR` | 笔记文件目录 |
| `WEBHOOK_URL` | 企业微信 Webhook |

---

## 9. 已完成功能

| 模块 | 功能 | 状态 |
|------|------|------|
| 🔐 访问码 | 全站访问码保护，分享链接 `?code=xxx` 自动验证 | ✅ |
| 个人主页 | 展示姓名、职位、头像、简介、技能、学习目标、联系方式 | ✅ |
| 登录认证 | JWT 认证、会话持久化（localStorage） | ✅ |
| 权限隔离 | 只能管理自己的资料和日志 | ✅ |
| 管理员 | 查看/删除所有用户和日志 | ✅ |
| 用户详情 | 点击成员卡片查看完整信息 | ✅ |
| 日志列表 | 按类型筛选、关键词搜索、分页浏览 | ✅ |
| 日志详情 | 查看完整内容、作者信息、标签展示 | ✅ |
| 创建日志 | 工作日志、学习日志、日报、周报、总结 5 种类型 | ✅ |
| 编辑/删除日志 | 仅作者可操作 | ✅ |
| 草稿自动保存 | 编辑日志时 2 秒防抖自动保存，关闭页面不丢失 | ✅ |
| 编辑资料 | 网页表单修改个人信息 | ✅ |
| 首页标签 | 成员/日志标签切换，自适应网格布局 | ✅ |
| 服务端持久化 | SQLite 数据库，重启不丢数据 | ✅ |
| 响应式设计 | 桌面端和移动端均可正常使用 | ✅ |
| Swagger 文档 | `/docs` 自动生成 API 文档 | ✅ |
| Docker 部署 | docker-compose 一键构建部署 | ✅ |
| 公网访问 | http://47.98.125.128 | ✅ |
| 日报 Agent | DeepSeek AI 自动将笔记整理为日报并发布 | ✅ |

---

## 10. 未完成内容与后续计划

| 项目 | 优先级 | 说明 |
|------|--------|------|
| Markdown 支持 | 中 | 日志内容目前为纯文本，计划支持 Markdown 渲染 |
| 评论/反馈 | 中 | 导师可在日志下留言反馈 |
| 图片上传 | 低 | 日志中支持插入图片 |
| 数据备份 | 中 | 定时将 SQLite 备份到云端 |
| CI/CD | 低 | GitHub Actions 自动构建测试和部署 |
| HTTPS | 高 | 配置 SSL 证书，启用 HTTPS |
| 域名绑定 | 低 | 绑定自定义域名代替 IP 地址 |
| Rate Limiting | 中 | 登录接口限速，防止暴力破解 |
| 数据库迁移 | 中 | 引入 Alembic 管理 Schema 变更 |

---

## 11. 本地运行

### 环境要求

- Python >= 3.10
- Node.js >= 18
- npm >= 9

### 手动启动

**启动后端**

```bash
cd backend

# 配置环境变量（首次运行）
cp .env.example .env
# 编辑 .env，设置 JWT_SECRET

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（首次运行：建表 + 种子数据）
python init_db.py

# 启动服务
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
| `lanxin` | `Lanxin@2026` | 管理员 |
| `zhangsan` | `Zhangsan@2026` | 普通用户 |

> ⚠️ 本地开发时访问码为 `mylog2026`（在 `backend/.env` 中配置）。
> 打开 http://localhost:5173?code=mylog2026 即可直接进入。

---

## 12. Docker 部署

### 环境变量

部署前需配置以下环境变量（或在 `docker compose up` 时传入）：

```bash
# 生成强随机 JWT 密钥
export JWT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
export ACCESS_CODE="your-access-code"
export CORS_ORIGINS="http://your-domain.com,https://your-domain.com"
```

### 部署命令

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

> 注意：数据库文件通过 Docker 卷 `mylog_data` 持久化。切勿使用 `docker compose down -v`（`-v` 会删除数据卷）。

### 分享链接

部署完成后，将以下链接分享给需要访问的人：

```
http://47.98.125.128?code=your-access-code
```

---

## 13. AI 使用说明

本项目使用 **Claude Code**（CLI AI 编程助手）辅助开发。AI 参与了以下环节：

| 环节 | AI 参与内容 |
|------|------------|
| 架构设计 | 技术选型讨论、数据库表结构设计、API 接口设计、Docker 部署方案、多用户升级方案、管理员功能设计、访问控制方案 |
| 代码生成 | 后端全部代码（FastAPI/SQLAlchemy CRUD、JWT 认证、权限隔离、访问码中间件）+ 前端全部代码（React 组件、AuthContext、路由守卫、AccessGate） |
| 安全审计 | 全面代码审查，修复 CORS、JWT 密钥、硬编码凭据、权限校验等 6 项严重安全问题 |
| 问题排查 | Python 版本兼容性、终端 GBK 编码、Windows venv 创建、passlib/bcrypt 兼容性（切换 PBKDF2）、FastAPI 422 验证错误处理、Docker 容器通信、SQLite 路径问题 |
| 文档编写 | 本 README 由 AI 辅助生成 |

所有 AI 生成的代码均经过本地运行验证和人工审查。

---

## License

MIT
