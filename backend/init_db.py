"""Initialize the database — create tables and insert seed data."""
from database import engine, SessionLocal, Base
from models import Profile, Post


def init():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables created.")

    db = SessionLocal()
    try:
        # Seed profile if not exists
        if not db.query(Profile).filter(Profile.id == 1).first():
            profile = Profile(
                id=1,
                name="兰鑫",
                title="智能体开发实习生",
                bio="热爱技术，喜欢用代码解决问题。目前正在学习全栈开发，目标是成为一名优秀的全栈工程师。",
                skills='["Python", "Java", "React", "Git", "Linux", "MySQL"]',
                github_url="https://github.com/Lanx111",
                blog_url="https://Lanx111.com/blog",
                email="2655453721@qq.com",
                learning_goals="深入学习 React 生态、掌握 FastAPI 后端开发、了解 Docker 容器化部署",
            )
            db.add(profile)

        # Seed some example posts
        if db.query(Post).count() == 0:
            examples = [
                Post(
                    title="入职第一天：环境搭建",
                    content="今天完成了开发环境搭建：\n1. 安装 VS Code 和必要插件\n2. 配置 Git 和 SSH\n3. 克隆项目代码\n4. 阅读项目 README\n\n遇到的问题：Python 版本冲突，通过 py 启动器解决。",
                    post_type="work_log",
                    tags='["入职", "环境搭建", "工具"]',
                ),
                Post(
                    title="React Hooks 学习笔记",
                    content="学习了 React 核心 Hooks：\n- useState：管理组件状态\n- useEffect：处理副作用\n- useContext：跨组件共享数据\n- useRef：引用 DOM 元素\n\n明天计划用这些 Hooks 重构之前的 class 组件。",
                    post_type="study_log",
                    tags='["React", "Hooks", "前端"]',
                ),
                Post(
                    title="2026-06-09 日报",
                    content="今日完成：\n1. 完成个人主页项目的需求分析\n2. 设计数据库表结构\n3. 搭建前后端项目脚手架\n\n明日计划：\n1. 实现后端 API\n2. 开始前端页面开发\n\n遇到的问题：\n- 前端技术选型犹豫，最终确定 Vite + React",
                    post_type="daily_report",
                    tags='["日报", "项目启动"]',
                ),
            ]
            db.add_all(examples)

        db.commit()
        print("[OK] Seed data inserted.")

        # Show summary
        profile = db.query(Profile).first()
        post_count = db.query(Post).count()
        if profile:
            print(f"  Profile: {profile.name} ({profile.title})")
        print(f"  Posts: {post_count}")

    finally:
        db.close()


if __name__ == "__main__":
    init()
