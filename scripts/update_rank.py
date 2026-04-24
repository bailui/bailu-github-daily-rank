import os
import re
import requests
from datetime import datetime, timezone

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

AUDIENCE_TIPS = {
    "AI工具": "适合想提升工作效率、做内容、写代码或研究 AI 应用的人。",
    "效率神器": "适合每天办公、写作、整理资料、自动化处理重复工作的用户。",
    "图片视频": "适合自媒体、设计师、剪辑师、博主和内容创作者。",
    "学习资源": "适合学生、转行者、程序员和想系统学习新技能的人。",
    "投资加密": "适合关注金融科技、量化交易、Web3 和加密工具的人。",
    "开发工具": "适合开发者、站长、独立开发者和技术创业者。",
    "值得关注": "适合喜欢发现新工具、新项目和新机会的人。",
}


def fetch_repos():
    repos = {}
    headers = {"Accept": "application/vnd.github+json"}
    for q in QUERIES:
        params = {"q": q, "sort": "updated", "order": "desc", "per_page": 20}
        try:
            r = requests.get("https://api.github.com/search/repositories", params=params, headers=headers, timeout=20)
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
    if any(x in desc.lower() for x in ["ai", "chatgpt", "llm", "agent", "automation", "awesome", "video", "image"]):
        score += 500
    return score


def clean_desc(desc, limit=110):
    desc = (desc or "暂无简介").replace("|", " ").replace("\n", " ").strip()
    return desc[:limit] + ("..." if len(desc) > limit else "")


def repo_cn_comment(repo):
    category = classify(repo)
    stars = repo.get("stargazers_count", 0)
    desc = (repo.get("description") or "").lower()
    if "awesome" in repo.get("name", "").lower() or "awesome" in desc:
        return "像一份高质量收藏夹，适合保存下来慢慢看。"
    if category == "AI工具":
        return "今天值得看，可能帮你把写作、编程、资料整理或自动化效率拉高。"
    if category == "图片视频":
        return "内容创作者可以重点看看，可能直接影响做图、剪辑或素材生产效率。"
    if category == "效率神器":
        return "适合日常办公和个人工作流优化，实用性通常比较强。"
    if category == "投资加密":
        return "适合研究工具逻辑，不建议直接照搬用于真实交易。"
    if stars > 50000:
        return "Star 很高，说明已经被大量用户验证，适合优先了解。"
    return "近期活跃，值得加入观察清单。"


def top_repos(repos, n=15):
    return sorted(repos, key=hot_score, reverse=True)[:n]


def generate_table(repos):
    rows = []
    for i, repo in enumerate(top_repos(repos), 1):
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
    lines = []
    for repo in top_repos(repos, 3):
        lines.append(f"- **[{repo['full_name']}]({repo['html_url']})**：{repo_cn_comment(repo)}  ")
        lines.append(f"  - 看点：{clean_desc(repo.get('description'), 90)}")
    return "\n".join(lines)


def generate_daily_article(repos, date):
    selected = top_repos(repos, 10)
    lines = [
        f"# 今日值得看的 10 个 GitHub 开源项目｜{date}",
        "",
        "每天从 GitHub 上筛选一批更适合大众关注的开源项目，重点看 AI 工具、效率神器、学习资源、图片视频、投资加密和开发工具。",
        "",
        "## 今日精选",
        "",
        generate_highlights(repos),
        "",
        "## 今日榜单",
        "",
    ]
    for i, repo in enumerate(selected, 1):
        category = classify(repo)
        lines.extend([
            f"### {i}. [{repo['full_name']}]({repo['html_url']})",
            "",
            f"- 分类：{category}",
            f"- 语言：{repo.get('language') or '-'}",
            f"- Stars：{repo.get('stargazers_count', 0):,}",
            f"- 一句话：{clean_desc(repo.get('description'), 160)}",
            f"- 为什么值得看：{repo_cn_comment(repo)}",
            f"- 适合人群：{AUDIENCE_TIPS.get(category, AUDIENCE_TIPS['值得关注'])}",
            "",
        ])
    lines.extend([
        "## 写在最后",
        "",
        "开源项目每天都在变化。这个榜单不追求只给程序员看，而是希望把真正有用、有趣、有潜力的工具筛出来，让普通用户、创作者、独立开发者和学习者都能发现新机会。",
        "",
        "> 本内容由 GitHub Actions 自动生成，仅用于学习研究和工具发现，不构成投资建议。",
    ])
    return "\n".join(lines)


def generate_xiaohongshu(repos, date):
    selected = top_repos(repos, 5)
    lines = [
        f"今天这 5 个 GitHub 项目值得收藏｜{date}",
        "",
        "每天帮你从 GitHub 里捞真正有用的开源工具，不只程序员能看，做内容、办公、学习、AI 副业都可能用得上。",
        "",
    ]
    for i, repo in enumerate(selected, 1):
        lines.append(f"{i}. {repo['full_name']}")
        lines.append(f"看点：{repo_cn_comment(repo)}")
        lines.append(f"适合：{AUDIENCE_TIPS.get(classify(repo), AUDIENCE_TIPS['值得关注'])}")
        lines.append("")
    lines.extend([
        "建议先收藏，再慢慢试。真正有价值的工具，往往不是刷到一次就会用，而是某一天刚好能帮你解决问题。",
        "",
        "#AI工具 #开源项目 #效率工具 #GitHub #自媒体工具 #学习资源 #独立开发",
    ])
    return "\n".join(lines)


def replace_block(content, start, end, body):
    return re.sub(f"{re.escape(start)}.*?{re.escape(end)}", f"{start}\n\n{body}\n\n{end}", content, flags=re.S)


def update_readme(repos, date):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
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


def write_outputs(repos, date):
    os.makedirs("docs", exist_ok=True)
    os.makedirs("content/xiaohongshu", exist_ok=True)
    with open(f"docs/{date}.md", "w", encoding="utf-8") as f:
        f.write(generate_daily_article(repos, date))
    with open(f"content/xiaohongshu/{date}.md", "w", encoding="utf-8") as f:
        f.write(generate_xiaohongshu(repos, date))


if __name__ == "__main__":
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    repos = fetch_repos()
    if not repos:
        raise SystemExit("No repositories fetched")
    update_readme(repos, date)
    write_outputs(repos, date)
