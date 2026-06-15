"""Initialize database — create tables and insert seed demo users."""
from database import engine, SessionLocal, Base
from models import User, Post
from crud import create_user, upsert_profile, create_post


def init():
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables created.")

    db = SessionLocal()
    try:
        # Create demo users if they don't exist
        if db.query(User).count() == 0:
            # User 1: Lan Xin (admin)
            user1 = create_user(db, "lanxin", "Lanxin@2026")
            user1.is_admin = True
            db.commit()
            upsert_profile(db, user1.id, {
                "name": "兰鑫",
                "title": "智能体开发实习生",
                "bio": "热爱技术，喜欢用代码解决问题。目前正在学习全栈开发，目标是成为一名优秀的全栈工程师。",
                "skills": ["Python", "Java", "React", "Git", "Linux", "MySQL"],
                "github_url": "https://github.com/Lanx111",
                "blog_url": "https://Lanx111.com/blog",
                "email": "2655453721@qq.com",
                "learning_goals": "深入学习 React 生态、掌握 FastAPI 后端开发、了解 Docker 容器化部署",
            })
            create_post(db, user1.id, {
                "title": "入职第一周：环境搭建与项目启动",
                "content": "本周完成了：\n1. 开发环境搭建\n2. MyLog 项目架构设计\n3. React + FastAPI 技术选型\n4. 本地开发流程跑通\n\n遇到的问题：Python 版本冲突，通过 py 启动器解决。",
                "post_type": "work_log",
                "tags": ["入职", "环境搭建"],
            })
            create_post(db, user1.id, {
                "title": "React Hooks 学习笔记",
                "content": "核心 Hooks：\n- useState：管理组件状态\n- useEffect：处理副作用\n- useContext：跨组件共享数据\n- useRef：引用 DOM 元素",
                "post_type": "study_log",
                "tags": ["React", "Hooks", "前端"],
            })

            # User 2: Zhang San (demo mentor)
            user2 = create_user(db, "zhangsan", "Zhangsan@2026")
            upsert_profile(db, user2.id, {
                "name": "张三",
                "title": "技术导师",
                "bio": "10 年后端开发经验，关注技术成长和团队协作。",
                "skills": ["Go", "Java", "Kubernetes", "Docker", "系统设计"],
                "github_url": "https://github.com/example",
                "email": "zhangsan@example.com",
                "learning_goals": "帮助实习生成长",
            })
            create_post(db, user2.id, {
                "title": "实习生入职观察记录",
                "content": "兰鑫本周完成了环境搭建和项目初始化，学习态度积极。\n\n建议：\n1. 多关注代码规范\n2. 可以开始了解 CI/CD 流程",
                "post_type": "summary",
                "tags": ["实习生", "反馈"],
            })

            print("[OK] Seed data inserted.")
        else:
            print("[OK] Database already has users, skipping seed.")

        user_count = db.query(User).count()
        post_count = db.query(Post).count()
        print(f"  Users: {user_count}, Posts: {post_count}")

    finally:
        db.close()


if __name__ == "__main__":
    init()
