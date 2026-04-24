import re
import requests
from datetime import datetime, timezone

# 免费版：不依赖第三方付费 API，不需要额外 Token。
# 思路：抓取近期活跃、Star 数较高、普通用户也容易感兴趣的开源项目。
# 重点从 AI 工具、效率工具、图片视频、学习资源、生活实用、加密与投资工具中筛选。

QUERIES = [
    "stars:>500 pushed:>2025-01-01 ai OR chatgpt OR llm OR agent",
    "stars:>500 pushed:>2025-01-01 productivity OR tool OR automation",
    "stars:>500 pushed:>2025-01-01 image OR video OR music OR design",
    "stars:>500 pushed:>2025-01-01 finance OR crypto OR trading OR stock",
    "stars:>500 pushed:>2025-01-01 awesome OR learning OR tutorial",
]

CATEGORY_RULES = {
    "AI工具": ["ai", "gpt", "chatgpt", "llm", "agent", "rag", "copilot"],
    "效率神器": ["productivity", "automation", "workflow", "tool", "cli", "note", "todo"],
    "图片视频": ["image", "video", "photo", "music", "audio", "design", "drawing"],
    "学习资源": ["awesome", "learning", "tutorial", "course", "book", "roadmap"],
    "投资加密": ["crypto", "trading", "stock", "finance", "quant", "bitcoin", "web3"],
    "开发工具": ["framework", "database", "frontend", "backend", "api", "server"],
}


def fetch_repos():
    repos = {}
    for q in QUERIES:
        url = "https://api.github.com/search/repositories"
        params = {"q": q, "sort": "updated", "order": "desc", "per_page": 20}
        try:
            r = requests.get(url, params=params, timeout=20)
            r.raise_for_status()
            for repo in r.json().get("items", []):
                repos[repo["full_name"]] = repo
        except Exception as e:
            print(f"Fetch failed: {q} -> {e}")
    return list(repos.values())


def classify(repo):
    text = f"{repo.get('name','')} {repo.get('description') or ''} {repo.get('topics') or ''}".lower()
    for category, words in CATEGORY_RULES.items():
        if any(w in text for w in words):
            return category
    return "值得关注"


def hot_score(repo):
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    watchers = repo.get("watchers_count", 0)
    desc = repo.get("description") or ""
    topics = repo.get("topics") or []
    score = stars * 0.58 + forks * 0.24 + watchers * 0.12 + len(topics) * 30
    if any(x in desc.lower() for x in ["ai", "chatgpt", "llm", "agent", "automation", "awesome"]):
        score += 500
    return score


def clean_desc(desc):
    desc = (desc or "暂无简介").replace("|", " ").replace("\n", " ").strip()
    return desc[:120] + ("..." if len(desc) > 120 else "")


def generate_table(repos):
    repos = sorted(repos, key=hot_score, reverse=True)[:15]
    rows = []
    for i, repo in enumerate(repos, 1):
        name = repo["full_name"]
        url = repo["html_url"]
        category = classify(repo)
        desc = clean_desc(repo.get("description"))
        lang = repo.get("language") or "-"
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        updated = repo.get("updated_at", "")[:10]
        rows.append(f"| {i} | [{name}]({url}) | {category} | {desc} | {lang} | {stars:,} | {forks:,} | {updated} |")
    return "\n".join(rows)


def generate_highlights(repos):
    repos = sorted(repos, key=hot_score, reverse=True)[:3]
    lines = []
    for repo in repos:
        lines.append(f"- **[{repo['full_name']}]({repo['html_url']})**：{clean_desc(repo.get('description'))}")
    return "\n".join(lines)


def replace_block(content, start, end, body):
    return re.sub(f"{re.escape(start)}.*?{re.escape(end)}", f"{start}\n\n{body}\n\n{end}", content, flags=re.S)


def update_readme(repos):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rank_body = (
        f"> 更新时间：{date}  ·  免费自动版  ·  面向大众关注的 AI、效率、学习、图片视频、投资加密工具\n\n"
        "### 今日精选\n\n"
        f"{generate_highlights(repos)}\n\n"
        "### 今日大众热门开源项目\n\n"
        "| 排名 | 项目 | 分类 | 一句话看点 | 语言 | Stars | Forks | 更新 |\n"
        "|---:|---|---|---|---|---:|---:|---|\n"
        f"{generate_table(repos)}"
    )

    content = replace_block(content, "<!-- DAILY_RANK_START -->", "<!-- DAILY_RANK_END -->", rank_body)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    repos = fetch_repos()
    if not repos:
        raise SystemExit("No repositories fetched")
    update_readme(repos)
