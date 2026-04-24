import requests
import re
from datetime import datetime

URL = "https://api.github.com/search/repositories?q=stars:>50&sort=updated&order=desc&per_page=20"

KEYWORDS = {
    "AI": ["ai", "gpt", "llm", "agent"],
    "Crypto": ["crypto", "blockchain", "web3"],
    "Dev": ["tool", "cli", "framework"],
    "Legal": ["law", "legal", "contract"]
}


def fetch_data():
    res = requests.get(URL)
    return res.json().get("items", [])


def classify(repo):
    text = (repo["name"] + " " + (repo["description"] or "")).lower()
    for k, words in KEYWORDS.items():
        if any(w in text for w in words):
            return k
    return "Other"


def generate_table(repos):
    lines = []
    for i, repo in enumerate(repos, 1):
        name = repo["full_name"]
        desc = (repo["description"] or "").replace("|", " ")
        lang = repo.get("language", "-")
        stars = repo["stargazers_count"]
        updated = repo["updated_at"][:10]
        tag = classify(repo)
        lines.append(f"| {i} | `{name}` | {tag} | {desc} | {lang} | {stars} | {updated} |")
    return "\n".join(lines)


def update_readme(table):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start = "<!-- DAILY_RANK_START -->"
    end = "<!-- DAILY_RANK_END -->"

    new_section = f"{start}\n\n| 排名 | 项目 | 分类 | 简介 | 语言 | Stars | 更新时间 |\n|---:|---|---|---|---|---:|---|\n{table}\n\n{end}"

    content = re.sub(f"{start}.*?{end}", new_section, content, flags=re.S)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    repos = fetch_data()
    table = generate_table(repos)
    update_readme(table)
