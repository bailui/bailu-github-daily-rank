import requests
from datetime import datetime

URL = "https://api.github.com/search/repositories?q=stars:>1&sort=stars&order=desc&per_page=10"


def fetch_data():
    res = requests.get(URL)
    data = res.json()
    return data.get("items", [])


def generate_table(repos):
    lines = []
    for i, repo in enumerate(repos, 1):
        name = repo["full_name"]
        desc = (repo["description"] or "").replace("|", " ")
        lang = repo.get("language", "-")
        stars = repo["stargazers_count"]
        forks = repo["forks_count"]
        updated = repo["updated_at"][:10]
        lines.append(f"| {i} | `{name}` | {desc} | {lang} | {stars} | {forks} | {updated} |")
    return "\n".join(lines)


def update_readme(table):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start = "<!-- DAILY_RANK_START -->"
    end = "<!-- DAILY_RANK_END -->"

    new_section = f"{start}\n\n| 排名 | 项目 | 简介 | 语言 | Stars | Forks | 更新时间 |\n|---:|---|---|---|---:|---:|---|\n{table}\n\n{end}"

    import re
    content = re.sub(f"{start}.*?{end}", new_section, content, flags=re.S)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    repos = fetch_data()
    table = generate_table(repos)
    update_readme(table)
