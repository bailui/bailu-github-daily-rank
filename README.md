<div align="center">

<img src="assets/banner.svg" alt="白鹿 GitHub 每日开源趋势榜" width="100%" />

# 白鹿 GitHub 每日开源趋势榜

每天自动发现 GitHub 上 **普通人也看得懂、用得上、值得收藏** 的开源项目。  
聚焦 **AI 工具、效率神器、学习资源、图片视频、投资加密、开发工具**。

[![Daily Update](https://github.com/bailui/bailu-github-daily-rank/actions/workflows/daily.yml/badge.svg)](https://github.com/bailui/bailu-github-daily-rank/actions/workflows/daily.yml)
![GitHub last commit](https://img.shields.io/github/last-commit/bailui/bailu-github-daily-rank?style=flat-square)
![GitHub Repo stars](https://img.shields.io/github/stars/bailui/bailu-github-daily-rank?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)

**每天 08:30 自动更新｜适合收藏｜适合做选题｜适合发现工具和机会**

</div>

---

## 🔥 这个项目适合谁每天看

- 想发现好用 AI 工具的人
- 想提升办公、写作、学习效率的人
- 想找自媒体、图片、视频工具的人
- 想关注加密货币、量化交易、金融科技工具的人
- 想找项目灵感、网站灵感、副业灵感的人
- 想每天快速浏览科技热点的人

---

## 📌 每天自动生成什么

本仓库每天会自动生成三类内容：

```text
README.md                      今日精选榜单
docs/YYYY-MM-DD.md             博客文章版
content/xiaohongshu/YYYY-MM-DD.md  小红书/自媒体文案版
```

---

## 今日趋势榜

<!-- DAILY_RANK_START -->

| 排名 | 项目 | 简介 | 语言 | Stars | Forks | 更新时间 |
|---:|---|---|---|---:|---:|---|
| 1 | `codecrafters-io/build-your-own-x` | Master programming by recreating your favorite technologies from scratch. | Markdown | 493781 | 46757 | 2026-04-24 |
| 2 | `sindresorhus/awesome` | 😎 Awesome lists about all kinds of interesting topics | None | 458409 | 34437 | 2026-04-24 |
| 3 | `freeCodeCamp/freeCodeCamp` | freeCodeCamp.org's open-source codebase and curriculum. Learn math, programming, and computer science for free. | TypeScript | 443456 | 44367 | 2026-04-24 |
| 4 | `public-apis/public-apis` | A collective list of free APIs | Python | 426108 | 46480 | 2026-04-24 |
| 5 | `EbookFoundation/free-programming-books` | :books: Freely available programming books | Python | 385948 | 66123 | 2026-04-24 |
| 6 | `openclaw/openclaw` | Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞  | TypeScript | 363045 | 74209 | 2026-04-24 |
| 7 | `kamranahmedse/developer-roadmap` | Interactive roadmaps, guides and other educational content to help developers grow in their careers. | TypeScript | 353492 | 43965 | 2026-04-24 |
| 8 | `donnemartin/system-design-primer` | Learn how to design large-scale systems. Prep for the system design interview.  Includes Anki flashcards. | Python | 343899 | 55525 | 2026-04-24 |
| 9 | `jwasham/coding-interview-university` | A complete computer science study plan to become a software engineer. | None | 342117 | 82088 | 2026-04-24 |
| 10 | `vinta/awesome-python` | An opinionated list of Python frameworks, libraries, tools, and resources | Python | 294092 | 27765 | 2026-04-24 |

<!-- DAILY_RANK_END -->

---

## 项目数据图

<div align="center">

<img src="assets/stats.svg" alt="趋势榜统计图" width="100%" />

</div>

---

## 🧭 内容入口

- 每日博客文章：[`docs/`](docs/)
- 小红书文案素材：[`content/xiaohongshu/`](content/xiaohongshu/)
- 主站规划：`https://www.bailuioai.com/`
- 后续可接入：博客、导航站、AI 工具合集、量化工具合集

---

## 自动更新机制

本项目每天北京时间 **08:30** 自动运行：

```mermaid
flowchart LR
    A[GitHub Actions 定时触发] --> B[抓取大众关注项目]
    B --> C[分类与热度评分]
    C --> D[生成 README / 博客 / 自媒体文案]
    D --> E[自动提交到仓库]
```

---

## 免责声明

本项目仅用于开源项目观察、学习研究和工具发现。榜单不构成投资建议、交易建议或法律意见。涉及加密货币、金融交易或第三方工具时，请自行审慎判断风险。

---

<div align="center">

由 **白鹿 io** 持续维护。  
让好项目被看见，让普通人也能读懂技术趋势。

</div>
