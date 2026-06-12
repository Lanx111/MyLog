"""
日报 Agent：读取今日笔记 → DeepSeek 优化 → 发布到 MyLog

使用方式：
  python daily_report.py              # 处理今天的笔记
  python daily_report.py 6.12          # 处理指定日期的笔记
"""
import sys
import os
import json
import urllib.request
from datetime import datetime
from pathlib import Path

# 用 httpx (已在 venv 中) 替代 requests
import httpx

# ─── 读取 .env 配置 ─────────────────────────────────

def _load_env():
    """简单解析 .env 文件，无需 pip install python-dotenv"""
    env = {}
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip()
    return env

_env = _load_env()

NOTES_DIR     = _env.get("NOTES_DIR", r"D:\NOTES\编程笔记\实习")
MYLOG_URL     = _env.get("MYLOG_URL", "http://47.98.125.128")
MYLOG_USER    = _env.get("MYLOG_USER", "lanxin")
MYLOG_PASS    = _env.get("MYLOG_PASS", "123456")

DEEPSEEK_KEY   = _env.get("DEEPSEEK_KEY", "")
DEEPSEEK_BASE  = _env.get("DEEPSEEK_BASE", "https://api.deepseek.com/anthropic")
DEEPSEEK_MODEL = _env.get("DEEPSEEK_MODEL", "deepseek-v4-pro[1m]")


# ─── 1. 读取今日笔记 ────────────────────────────────

def get_today_filename(date_str: str | None = None) -> Path:
    if date_str:
        parts = date_str.replace("-", ".").split(".")
        if len(parts) == 2:
            month, day = parts[0], parts[1]
        elif len(parts) == 3:
            month, day = parts[1], parts[2]
        else:
            raise ValueError(f"无法解析日期: {date_str}")
    else:
        today = datetime.now()
        month, day = str(today.month), str(today.day)

    return Path(NOTES_DIR) / f"{month}.{day}.txt"


def read_notes(filepath: Path) -> str:
    if not filepath.exists():
        raise FileNotFoundError(f"笔记文件不存在: {filepath}")
    return filepath.read_text(encoding="utf-8")


# ─── 2. DeepSeek 优化 (Anthropic Messages API 格式) ──

def optimize_with_deepseek(raw_notes: str) -> dict:
    if not DEEPSEEK_KEY:
        raise RuntimeError("请在 .env 中设置 DEEPSEEK_KEY")

    prompt = f"""请把以下工作笔记整理成一份规范的日报，包含三部分：
1. 今日完成
2. 遇到的问题
3. 明日计划

直接输出日报正文，不要加额外说明。如果某部分没有信息，填写"无"。

以下是我的笔记：

{raw_notes}"""

    body = json.dumps({
        "model": DEEPSEEK_MODEL,
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    url = f"{DEEPSEEK_BASE}/v1/messages"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", DEEPSEEK_KEY)
    req.add_header("anthropic-version", "2023-06-01")

    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode("utf-8")

    result = json.loads(raw)

    # 找 type="text" 的 content block（跳过 thinking）
    text_blocks = [b for b in result.get("content", []) if b.get("type") == "text"]
    content = text_blocks[0].get("text", "") if text_blocks else ""
    if not content:
        raise RuntimeError(f"无法解析响应: {raw[:300]}")

    content = content.strip()

    today_str = datetime.now().strftime("%m.%d")
    return {"title": f"{today_str} 日报", "content": content}


# ─── 3. 发布到 MyLog ────────────────────────────────

def login_mylog() -> str:
    with httpx.Client() as client:
        resp = client.post(
            f"{MYLOG_URL}/api/auth/login",
            json={"username": MYLOG_USER, "password": MYLOG_PASS},
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"登录失败: {data.get('message')}")
        return data["data"]["access_token"]


def post_daily_report(token: str, title: str, content: str) -> dict:
    with httpx.Client() as client:
        resp = client.post(
            f"{MYLOG_URL}/api/posts",
            json={
                "title": title,
                "content": content,
                "post_type": "daily_report",
                "tags": ["日报", "AI 生成"],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        return resp.json()


# ─── 主流程 ─────────────────────────────────────────

def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else None

    print("1. 读取笔记...")
    filepath = get_today_filename(date_str)
    raw_notes = read_notes(filepath)
    print(f"   文件: {filepath}")
    print(f"   字数: {len(raw_notes)} 字\n")

    print("2. DeepSeek 优化中...")
    report = optimize_with_deepseek(raw_notes)
    print(f"   标题: {report['title']}")
    print(f"   内容:\n{report['content'][:300]}\n")

    print("3. 发布到 MyLog...")
    token = login_mylog()
    result = post_daily_report(token, report["title"], report["content"])
    print(f"   状态: {result.get('message')}")
    print(f"   链接: {MYLOG_URL}/posts/{result['data']['id']}")
    print("\nDone!")


if __name__ == "__main__":
    main()
