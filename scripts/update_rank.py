import os
import re
import requests
from datetime import datetime, timezone

SITE_URL = "https://www.bailuioai.com/#blog"
REPO_URL = "https://github.com/bailui/bailu-github-daily-rank"

QUERIES = [
    "ai stars:>500 pushed:>2025-01-01",
    "chatgpt stars:>500 pushed:>2025-01-01",
    "productivity stars:>500 pushed:>2025-01-01",
    "image stars:>500 pushed:>2025-01-01",
    "awesome stars:>500 pushed:>2025-01-01",
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

CATEGORY_EN = {
    "AI工具": "AI Tools",
    "效率神器": "Productivity",
    "图片视频": "Image & Video",
    "学习资源": "Learning",
    "投资加密": "Finance & Crypto",
    "开发工具": "Dev Tools",
    "值得关注": "Worth Watching",
}

CATEGORY_JA = {
    "AI工具": "AIツール",
    "效率神器": "生産性ツール",
    "图片视频": "画像・動画",
    "学习资源": "学習リソース",
    "投资加密": "金融・暗号資産",
    "开发工具": "開発ツール",
    "值得关注": "注目プロジェクト",
}

CATEGORY_KO = {
    "AI工具": "AI 도구",
    "效率神器": "생산성 도구",
    "图片视频": "이미지·비디오",
    "学习资源": "학습 자료",
    "投资加密": "금융·크립토",
    "开发工具": "개발 도구",
    "值得关注": "주목할 프로젝트",
}


def fetch_repos():
    repos = {}
    headers = {"Accept": "application/vnd.github+json"}
    for q in QUERIES:
        params = {"q": q, "sort": "updated", "order": "desc", "per_page": 20}
        try:
            r = requests.get("https://api.github.com/search/repositories", params=params, headers=headers, timeout=20)
            if r.status_code != 200:
                print(f"Fetch failed: {q} -> {r.status_code} {r.text[:200]}")
                continue
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


def escape_ts(text):
    return (text or "").replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def repo_cn_comment(repo):
    category = classify(repo)
    stars = repo.get("stargazers_count", 0)
    desc = (repo.get("description") or "").lower()
    if "awesome" in repo.get("name", "").lower() or "awesome" in desc:
        return "我会把它当作资料库收藏，适合慢慢翻。"
    if category == "AI工具":
        return "我会优先关注这类项目，它可能直接改变写作、编程、整理资料和自动化工作的效率。"
    if category == "图片视频":
        return "这类项目对内容创作者很实用，可能直接影响做图、剪辑或素材生产效率。"
    if category == "效率神器":
        return "这类项目值得放进日常工作流里观察，实用性通常比较强。"
    if category == "投资加密":
        return "我会把它作为工具和思路参考，不建议未经验证就用于真实交易。"
    if stars > 50000:
        return "这个项目已经被大量用户验证，值得优先了解。"
    return "近期比较活跃，我会先放进观察清单。"


def repo_en_comment(repo):
    category = classify(repo)
    if category == "AI工具":
        return "My take: worth tracking because it may improve writing, coding, research, or automation workflows."
    if category == "图片视频":
        return "My take: useful for creators who work with images, videos, audio, or design assets."
    if category == "效率神器":
        return "My take: this could become part of a practical daily productivity workflow."
    if category == "学习资源":
        return "My take: a good project to bookmark and revisit when learning or building a roadmap."
    if category == "投资加密":
        return "My take: useful for research, but not something to copy directly into real trading without verification."
    return "My take: an active project worth adding to a watchlist."


def repo_ja_comment(repo):
    category = classify(repo)
    if category == "AI工具":
        return "所感：文章作成、開発、調査、自動化の効率を上げる可能性があり、継続的に見たいプロジェクトです。"
    if category == "图片视频":
        return "所感：画像、動画、音声、デザイン系の制作に関わる人には参考になります。"
    if category == "效率神器":
        return "所感：日々の作業フローに入れられる可能性がある実用系ツールです。"
    if category == "学习资源":
        return "所感：学習ロードマップや資料集として保存しておきたいプロジェクトです。"
    return "所感：活発に更新されており、ウォッチリストに入れておきたいプロジェクトです。"


def repo_ko_comment(repo):
    category = classify(repo)
    if category == "AI工具":
        return "의견: 글쓰기, 개발, 리서치, 자동화 효율을 높일 수 있어 계속 지켜볼 만합니다."
    if category == "图片视频":
        return "의견: 이미지, 영상, 오디오, 디자인 작업을 하는 사람에게 유용할 수 있습니다."
    if category == "效率神器":
        return "의견: 일상 업무 흐름에 넣어볼 만한 실용 도구입니다."
    if category == "学习资源":
        return "의견: 학습 자료나 로드맵으로 저장해두기 좋습니다."
    return "의견: 최근 활발히 업데이트되는 프로젝트로 관찰할 가치가 있습니다."


def top_repos(repos, n=15):
    return sorted(repos, key=hot_score, reverse=True)[:n]


def generate_personal_take(repos):
    top = top_repos(repos, 3)
    lines = [
        "### 我的今日观察",
        "",
        "今天我会重点看这几个方向：AI 工具是否真的能进入日常工作流，效率工具是否足够简单可用，以及学习资源是否适合长期收藏。",
        "",
    ]
    for repo in top:
        lines.append(f"- [{repo['full_name']}]({repo['html_url']})：{repo_cn_comment(repo)}")
    lines.extend(["", f"完整项目与每日归档：[{REPO_URL}]({REPO_URL})", f"网站阅读入口：[{SITE_URL}]({SITE_URL})"])
    return "\n".join(lines)


def generate_table(repos):
    rows = []
    for i, repo in enumerate(top_repos(repos), 1):
        rows.append(f"| {i} | [{repo['full_name']}]({repo['html_url']}) | {classify(repo)} | {clean_desc(repo.get('description'))} | {repo.get('language') or '-'} | {repo.get('stargazers_count', 0):,} | {repo.get('forks_count', 0):,} | {repo.get('updated_at', '')[:10]} |")
    return "\n".join(rows)


def generate_multilang_tables(repos):
    selected = top_repos(repos, 10)
    def table(mapping, comment_fn, headers):
        rows = [headers]
        for i, repo in enumerate(selected, 1):
            category = mapping.get(classify(repo), "Worth Watching")
            rows.append(f"| {i} | [{repo['full_name']}]({repo['html_url']}) | {category} | {clean_desc(repo.get('description'), 90)} | {comment_fn(repo)} |")
        return "\n".join(rows)
    return "\n\n".join([
        "<details>\n<summary>English</summary>\n\n" + table(CATEGORY_EN, repo_en_comment, "| Rank | Project | Category | Description | My take |\n|---:|---|---|---|---|") + "\n\n</details>",
        "<details>\n<summary>日本語</summary>\n\n" + table(CATEGORY_JA, repo_ja_comment, "| 順位 | プロジェクト | カテゴリ | 説明 | 所感 |\n|---:|---|---|---|---|") + "\n\n</details>",
        "<details>\n<summary>한국어</summary>\n\n" + table(CATEGORY_KO, repo_ko_comment, "| 순위 | 프로젝트 | 카테고리 | 설명 | 의견 |\n|---:|---|---|---|---|") + "\n\n</details>",
    ])


def generate_highlights(repos):
    lines = []
    for repo in top_repos(repos, 3):
        lines.append(f"- **[{repo['full_name']}]({repo['html_url']})**：{repo_cn_comment(repo)}  ")
        lines.append(f"  - 看点：{clean_desc(repo.get('description'), 90)}")
    return "\n".join(lines)


def generate_daily_article(repos, date):
    lines = [f"# 今日值得看的 10 个 GitHub 开源项目｜{date}", "", f"阅读入口：[{SITE_URL}]({SITE_URL})", f"项目归档：[{REPO_URL}]({REPO_URL})", "", "每天从 GitHub 上筛选一批更适合大众关注的开源项目，重点看 AI 工具、效率工具、学习资源、图片视频、投资加密和开发工具。", "", generate_personal_take(repos), "", "## 今日精选", "", generate_highlights(repos), "", "## 今日榜单", ""]
    for i, repo in enumerate(top_repos(repos, 10), 1):
        category = classify(repo)
        lines.extend([f"### {i}. [{repo['full_name']}]({repo['html_url']})", "", f"- 地址：[{repo['html_url']}]({repo['html_url']})", f"- 分类：{category}", f"- 语言：{repo.get('language') or '-'}", f"- Stars：{repo.get('stargazers_count', 0):,}", f"- 一句话：{clean_desc(repo.get('description'), 160)}", f"- 我的判断：{repo_cn_comment(repo)}", f"- 适合人群：{AUDIENCE_TIPS.get(category, AUDIENCE_TIPS['值得关注'])}", ""])
    lines.extend(["## Multi-language quick view", "", generate_multilang_tables(repos), "", "## 写在最后", "", "开源项目每天都在变化。我会持续记录这些项目，重点看它们是否真的能解决问题、提升效率，或者带来新的产品和内容机会。", "", "> 本内容由 GitHub Actions 自动生成，并加入白鹿 io 的观察口径；仅用于学习研究和工具发现，不构成投资建议。"])
    return "\n".join(lines)


def generate_xiaohongshu(repos, date):
    lines = [f"今天这 5 个 GitHub 项目值得收藏｜{date}", "", "我每天会从 GitHub 里筛一批值得看的开源工具，重点看它们能不能提升效率、带来选题灵感，或者成为后续网站/产品的素材。", "", f"完整地址：{REPO_URL}", f"网站入口：{SITE_URL}", ""]
    for i, repo in enumerate(top_repos(repos, 5), 1):
        lines.append(f"{i}. {repo['full_name']}")
        lines.append(f"地址：{repo['html_url']}")
        lines.append(f"我的判断：{repo_cn_comment(repo)}")
        lines.append(f"适合：{AUDIENCE_TIPS.get(classify(repo), AUDIENCE_TIPS['值得关注'])}")
        lines.append("")
    lines.extend(["建议先收藏，再慢慢试。真正有价值的工具，往往不是刷到一次就会用，而是某一天刚好能帮你解决问题。", "", "#AI工具 #开源项目 #效率工具 #GitHub #自媒体工具 #学习资源 #独立开发"])
    return "\n".join(lines)


def generate_blogpost_ts(repos, date):
    article_html = generate_daily_article(repos, date).replace("\n", "<br/>\n")
    title = f"今日值得看的 10 个 GitHub 开源项目｜{date}"
    summary = "白鹿 io 每日开源观察：带个人判断、项目地址、多语言速览，筛选值得关注的 AI 工具、效率工具和学习资源。"
    lines = [
        "import { BlogPost } from '../types';",
        "",
        "export const githubDailyPosts: BlogPost[] = [",
        "  {",
        f"    id: 'github-daily-{date}',",
        f"    title: `{escape_ts(title)}`,",
        f"    summary: `{escape_ts(summary)}`,",
        f"    content: `{escape_ts(article_html)}`,",
        "    author: '白鹿 io',",
        f"    date: '{date}',",
        "    category: 'AI工具',",
        "    readCount: 0,",
        "    tags: ['GitHub', 'AI工具', '效率工具', '开源项目', '多语言'],",
        "    coverImage: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=800'",
        "  }",
        "];",
        "",
    ]
    return "\n".join(lines)


def replace_block(content, start, end, body):
    return re.sub(f"{re.escape(start)}.*?{re.escape(end)}", f"{start}\n\n{body}\n\n{end}", content, flags=re.S)


def update_readme(repos, date):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    rank_body = f"> 更新时间：{date}  ·  免费自动版  ·  带个人观察、项目直达链接和多语言速览\n\n{generate_personal_take(repos)}\n\n### 今日精选\n\n{generate_highlights(repos)}\n\n### 今日大众热门开源项目\n\n| 排名 | 项目 | 分类 | 一句话看点 | 语言 | Stars | Forks | 更新 |\n|---:|---|---|---|---|---:|---:|---|\n{generate_table(repos)}\n\n### 多语言速览 / Multi-language quick view\n\n{generate_multilang_tables(repos)}"
    content = replace_block(content, "<!-- DAILY_RANK_START -->", "<!-- DAILY_RANK_END -->", rank_body)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)


def write_outputs(repos, date):
    os.makedirs("docs", exist_ok=True)
    os.makedirs("content/xiaohongshu", exist_ok=True)
    os.makedirs("dist-site", exist_ok=True)
    with open(f"docs/{date}.md", "w", encoding="utf-8") as f:
        f.write(generate_daily_article(repos, date))
    with open(f"content/xiaohongshu/{date}.md", "w", encoding="utf-8") as f:
        f.write(generate_xiaohongshu(repos, date))
    with open("dist-site/githubDailyPosts.ts", "w", encoding="utf-8") as f:
        f.write(generate_blogpost_ts(repos, date))


if __name__ == "__main__":
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    repos = fetch_repos()
    if not repos:
        print("No repositories fetched from GitHub API. Keep previous README unchanged.")
        raise SystemExit(0)
    update_readme(repos, date)
    write_outputs(repos, date)
