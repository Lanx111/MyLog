# MyLog — 个人主页与成长日志系统

## 1. 项目简介

MyLog 是一个全栈 Web 应用，用于：

- **展示个人信息**：姓名、职位、技术方向、学习目标、联系方式
- **记录成长日志**：工作日志、学习日志、日报、周报、阶段总结
- **方便导师了解进展**：导师打开页面即可看到最近在做什么、遇到了什么问题、接下来计划做什么

技术栈：**React + Vite（前端） + FastAPI + SQLite（后端） + Docker（部署）**

线上地址：**http://47.98.125.128**

---

## 2. 如何本地启动

### 环境要求

- Python >= 3.8（推荐 3.10+）
- Node.js >= 18
- npm >= 9

### 方式一：一键启动（推荐）

```bash
# Windows
start.bat

# macOS / Linux / Git Bash
bash start.sh
```

### 方式二：手动启动

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

前端运行在 http://localhost:5173，Vite 自动代理 `/api` 到后端。

### 持久化服务说明

SQLite 数据库文件 `backend/mylog.db` 在首次运行 `python init_db.py` 时自动创建。数据直接存储在本地文件中，无需安装 MySQL/PostgreSQL 等外部数据库服务。关闭前后端后数据不会丢失，下次启动时自动加载。

---

## 3. 技术选型与原因

| 层级 | 技术 | 选择理由 |
|------|------|----------|
| 前端框架 | **React** | 实习要求使用 |
| 构建工具 | **Vite** | React 官方推荐的现代构建工具，启动快、HMR 优秀 |
| 路由 | **React Router v6** | React 生态最主流的路由方案 |
| 样式 | **CSS Modules** | 零依赖，组件级样式隔离 |
| 后端框架 | **FastAPI** | 自动生成 Swagger 文档、Pydantic 类型验证、原生异步支持 |
| ORM | **SQLAlchemy 2.0** | Python 最成熟的 ORM |
| 数据库 | **SQLite** | 零配置、无需安装服务、单文件存储、方便备份迁移 |
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

选择 SQLite 的原因：
- 零配置，无需安装数据库服务，本地开发和服务器部署都简单
- 单文件存储（`mylog.db`），方便备份：复制文件即可
- Docker 部署时使用命名卷（`mylog_data`）挂载，容器重启数据不丢失
- 对于个人主页和日志系统这种并发量低的场景，SQLite 完全够用

### 数据模型

**profile 表（个人信息，单行）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 固定为 1 |
| name | VARCHAR(100) | 姓名 |
| title | VARCHAR(200) | 职位/角色 |
| avatar_url | TEXT | 头像链接 |
| bio | TEXT | 个人简介 |
| skills | TEXT (JSON) | 技能标签数组 |
| github_url | TEXT | GitHub 主页 |
| blog_url | TEXT | 博客地址 |
| email | VARCHAR(200) | 邮箱 |
| learning_goals | TEXT | 当前学习目标 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**posts 表（日志）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| title | VARCHAR(300) | 标题 |
| content | TEXT | 正文 |
| post_type | VARCHAR(20) | 类型：work_log / study_log / daily_report / weekly_report / summary |
| tags | TEXT (JSON) | 标签数组 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 数据流

```
浏览器 (React)
    ↕ fetch /api/*
Nginx (前端容器 :80)
    ↕ proxy_pass
FastAPI (后端容器 :8000)
    ↕ SQLAlchemy ORM
SQLite (mylog.db，宿主机卷挂载)
```

所有数据通过 API 读写，核心内容不存储在 localStorage、sessionStorage 或前端 mock 数据中。

---

## 5. 我对需求的理解

这次实践的核心是：**构建一个导师能随时了解实习生进展的工具，而不仅仅是一个静态展示页。**

具体拆解为三个层次：

1. **"我是谁"** — 个人信息展示，让访问者快速了解技术背景和学习方向
2. **"我在做什么"** — 日志记录和查看，覆盖工作、学习、日报、周报等多种场景
3. **"怎么让导师看到"** — 服务端持久化 + 公网部署，换设备也能访问，多人可见

关键约束是：React 前端 + Python 后端 + 服务端持久化 + 线上可访问。不能走捷径（如纯前端 localStorage 方案）。

---

## 6. 核心用户流程

### 访客流程（导师/团队成员）

```
打开 http://47.98.125.128
    → 看到个人主页（姓名、技能、学习目标）
    → 看到最新 5 条日志
    → 点击「日志」进入列表页
    → 可按类型筛选（工作日志/学习日志/日报/周报/总结）
    → 可按关键词搜索
    → 翻页浏览历史日志
    → 点击某条日志查看详情
```

### 实习生流程（自己）

```
打开 http://47.98.125.128
    → 点击「管理」进入管理页
    → 编辑资料：修改姓名、技能、GitHub 等 → 保存
    → 写日志：选择类型、填写标题和内容、添加标签 → 发布
    → 日志列表中可编辑或删除已有日志
    → 返回首页确认更新
```

---

## 7. 已完成功能

| 模块 | 功能 | 状态 |
|------|------|------|
| 个人主页 | 展示姓名、职位、头像、简介、技能、学习目标、联系方式 | ✅ |
| 日志列表 | 按类型筛选、关键词搜索、分页浏览 | ✅ |
| 日志详情 | 查看完整内容、标签展示 | ✅ |
| 创建日志 | 支持工作日志、学习日志、日报、周报、总结 5 种类型 | ✅ |
| 编辑日志 | 修改标题、内容、类型、标签 | ✅ |
| 删除日志 | 确认后删除 | ✅ |
| 编辑资料 | 网页表单直接修改个人信息 | ✅ |
| 服务端持久化 | SQLite 数据库，重启不丢数据 | ✅ |
| 响应式设计 | 桌面端和移动端均可正常使用 | ✅ |
| Swagger 文档 | `/docs` 自动生成 API 文档 | ✅ |
| Docker 部署 | docker-compose 一键构建部署 | ✅ |
| 公网访问 | http://47.98.125.128 | ✅ |

---

## 8. 未完成内容与后续计划

| 项目 | 优先级 | 说明 |
|------|--------|------|
| 身份认证 | 高 | 目前管理页无登录保护，任何人可编辑。计划加入简单的密码认证或 JWT 登录 |
| Markdown 支持 | 中 | 日志内容目前为纯文本，计划支持 Markdown 渲染 |
| 评论/反馈 | 中 | 导师可在日志下留言反馈 |
| 数据备份 | 中 | 定时将 SQLite 备份到云端或 GitHub |
| 图片上传 | 低 | 日志中支持插入图片 |
| RSS 订阅 | 低 | 导师可通过 RSS 订阅日志更新 |
| CI/CD | 低 | GitHub Actions 自动构建和部署 |
| HTTPS | 低 | 配置 SSL 证书，启用 HTTPS |
| 域名绑定 | 低 | 绑定自定义域名代替 IP 地址 |

---

## 9. AI 使用说明

本项目使用 **Claude Code**（CLI AI 编程助手）辅助开发。AI 参与了以下环节：

| 环节 | AI 参与内容 |
|------|------------|
| 架构设计 | 讨论技术选型（React + FastAPI + SQLite）、数据库表结构、API 接口设计、Docker 部署方案 |
| 代码生成 | 生成后端全部代码（FastAPI/SQLAlchemy CRUD）和前端全部代码（React 组件和页面） |
| 问题排查 | 协助解决 Python 版本兼容性（3.6 → 3.10）、终端 GBK 编码问题、Windows venv 创建错误、Docker 容器通信问题 |
| 文档编写 | 本 README 由 AI 辅助生成 |

所有 AI 生成的代码均经过本地运行验证和人工审查。每一位技术决策和问题修复，开发者都需要理解原理并能独立解释。

人类开发者的核心工作在于：需求分析、产品设计、方案验证、代码审查和功能测试。

---

## 10. 线上访问地址

**http://47.98.125.128**

部署方式：Docker Compose on 阿里云 ECS

- 前端容器（Nginx + React）：80 端口对外
- 后端容器（FastAPI）：8000 端口（仅内部网络）
- 数据卷（SQLite）：宿主机持久化

---

## License

MIT
