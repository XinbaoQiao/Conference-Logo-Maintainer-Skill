<div align="center">

# Conference Logo Maintainer Skill

Maintain CCF conference logo assets with a one-shot code agent workflow.

<p>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-0f766e"></a>
  <img alt="Scope: CCF A/B/C" src="https://img.shields.io/badge/scope-CCF%20A%2FB%2FC-2563eb">
  <img alt="Mode: One Shot" src="https://img.shields.io/badge/mode-One--Shot-7c2d92">
  <img alt="Output: Logos and Reports" src="https://img.shields.io/badge/output-Logos%20%2B%20Reports-a21d16">
</p>

<p>
  <a href="#english">English</a> ·
  <a href="#zh-cn">中文</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#master-prompt">Master Prompt</a>
</p>

</div>

<a id="english"></a>

## English

Conference Logo Maintainer Skill helps a code agent maintain CCF conference logo assets end to end.

It is designed for users who want a clean, reusable logo asset set without manually visiting hundreds of conference websites or running maintenance scripts themselves.

### Highlights

| Feature | Why it helps |
|---|---|
| One-shot maintenance | The agent handles refresh, repair, audit, reporting, and optional downstream sync in one request. |
| CCF-focused coverage | The workflow targets CCF A/B/C conference records instead of arbitrary web search results. |
| Manual correction support | Confirmed logo URLs are used directly, while conferences marked as logo-unavailable remain intentionally blank. |
| False-positive resistance | The agent avoids speaker portraits, venue photos, sponsor marks, generic society logos, UI icons, and unrelated acronym matches. |
| Annual refresh tracking | Logos with year, city, or venue signals are surfaced for future updates. |
| White-logo warning | White or transparent logos are flagged because they may disappear on white backgrounds. |

### At A Glance

| You provide | The agent prepares |
|---|---|
| This skill repository | Updated CCF conference logo assets |
| Optional manual correction notes | Exact-logo overrides or intentionally blank entries |
| Optional downstream project path | Synchronized logo copy when available |
| One maintenance request | Final summary with asset counts, skipped entries, and remaining manual checks |

### What This Project Provides

| Area | What you get |
|---|---|
| Assets | Maintained CCF conference logo files under `assets/logos` |
| Metadata | A machine-readable manifest for downstream automation |
| Checklist | A human-readable maintenance list for missing or yearly-sensitive logos |
| Reports | Yearly-refresh priorities, white-logo warnings, and integrity audit results |
| Integration | Optional asset sync for Better-Poster-Skill when both projects are in the same workspace |

<a id="quick-start"></a>

### Quick Start

Install this repository as a Codex skill:

```bash
mkdir -p ~/.codex/skills
cp -R Conference-Logo-Maintainer-Skill ~/.codex/skills/conference-logo-maintainer
```

Then ask the code agent to update the conference logo assets:

```text
Use $conference-logo-maintainer to update the CCF conference logo assets.

Please complete the whole workflow automatically:
- refresh or repair conference logos;
- apply manual correction records;
- keep hard-to-resolve logo entries blank when required;
- flag year/city/venue-sensitive logos;
- flag white or transparent logos;
- sync the final assets to Better-Poster-Skill if available;
- report the final asset count, skipped entries, validation result, and remaining manual-review items.
```

The agent will use the skill instructions to complete the maintenance run and report the final result.

<a id="master-prompt"></a>

### Master Prompt

Copy this prompt into your code agent when you want a full one-shot maintenance run:

```text
You are maintaining the Conference Logo Maintainer Skill.

Goal:
Update the CCF conference logo assets end to end and produce a final, validated asset set.

Requirements:
1. Refresh CCF A/B/C conference logo assets using the existing Conference Logo Maintainer Skill logic.
2. Preserve confirmed good existing logos unless a better official source is found.
3. Apply manual correction records:
   - Conferences absent from manual corrections must continue through the normal automated tracking flow.
   - Conferences marked as having an exact logo must use the configured official logo URL or yearly URL template first.
   - Conferences marked as having only a website and no reliable logo must remain blank and must not be crawled.
4. Detect and avoid false positives such as speaker portraits, venue photos, sponsor marks, society logos, UI icons, and unrelated acronym matches.
5. Identify logos that should be prioritized for future yearly refresh because they contain year, city, or venue signals.
6. Identify white or transparent logos that may be invisible on white backgrounds and report them clearly.
7. Sync the final logo assets into the downstream project logo directory if one is present.
8. Validate that the maintained logo directory and downstream copy have matching file names and hashes.

Deliverables:
- Updated logo assets.
- Updated machine-readable manifest.
- Updated human-readable maintenance checklist.
- Updated yearly-refresh and white-logo watchlist report.
- Final summary with processed count, asset count, skipped/blank conferences, validation result, and any remaining manual review items.
```

### Outputs

Depending on workspace state and network access, the agent can return:

- Updated conference logo files.
- A machine-readable logo manifest.
- A human-readable maintenance checklist.
- A yearly-refresh priority report.
- A white-logo visual QA watchlist.
- A short summary of updated assets, intentionally blank entries, validation status, and remaining manual checks.

### User Check

Before using the logos in posters, websites, or redistributed assets, manually verify:

| Check | Why it matters |
|---|---|
| Logo identity | The asset should match the intended conference, not an organization, sponsor, speaker, or venue. |
| Year, city, and venue text | Annual conference logos may become stale quickly. |
| Background visibility | White or transparent logos may be invisible on white poster or web backgrounds. |
| Trademark and copyright | Conference branding may have redistribution or attribution requirements. |
| Downstream rendering | Always inspect the final poster, page, or asset bundle where the logo is used. |

### License

This repository is MIT licensed.

Review conference logo copyright, trademark, and attribution requirements before redistributing generated or downloaded logo files.

<p align="right"><a href="#conference-logo-maintainer-skill">Back to top</a> · <a href="#zh-cn">中文</a></p>

---

<a id="zh-cn"></a>

## 中文

Conference Logo Maintainer Skill 用于帮助 code agent 端到端维护 CCF 会议 Logo 资产。

它适合希望获得干净、可复用会议 Logo 资产集的用户，而不是手动访问上百个会议官网、手动运行维护脚本。

### 核心特点

| 特点 | 价值 |
|---|---|
| 一次请求完成维护 | agent 会在一次调用中完成刷新、修复、审计、报告生成和可选下游同步。 |
| 面向 CCF 会议范围 | 工作流聚焦 CCF A/B/C 会议记录，而不是泛化网页搜索结果。 |
| 支持手工修正 | 已确认的 Logo URL 会被优先使用；确认难以获取 Logo 的会议会被明确留空。 |
| 降低误匹配风险 | agent 会排除演讲者头像、会场照片、赞助商标识、泛组织 Logo、页面 UI 图标和无关缩写匹配。 |
| 跟踪年度更新目标 | 带有年份、城市或地点信息的 Logo 会被标记，方便后续年度刷新。 |
| 提醒白色 Logo 风险 | 白色或透明 Logo 会被单独提醒，因为它们在白底上可能不可见。 |

### 快速概览

| 你提供 | agent 生成 |
|---|---|
| 这个 skill 仓库 | 更新后的 CCF 会议 Logo 资产 |
| 可选的手工修正说明 | 精确 Logo 覆盖或明确留空条目 |
| 可选的下游项目路径 | 在可用时同步 Logo 副本 |
| 一次维护请求 | 包含资产数量、跳过条目和剩余人工检查项的最终汇报 |

### 这个项目提供什么

| 模块 | 内容 |
|---|---|
| 资产 | `assets/logos` 下维护好的 CCF 会议 Logo 文件 |
| 元数据 | 方便下游自动化读取的机器可读 manifest |
| 清单 | 面向人工维护的缺失项和年度敏感 Logo 检查列表 |
| 报告 | 年度更新优先级、白色 Logo 提醒和完整性审计结果 |
| 集成 | 当同一工作区存在 Better-Poster-Skill 时，可自动同步 Logo 资产 |

### 快速开始

先把本仓库安装为 Codex skill：

```bash
mkdir -p ~/.codex/skills
cp -R Conference-Logo-Maintainer-Skill ~/.codex/skills/conference-logo-maintainer
```

然后让 code agent 自动更新会议 Logo：

```text
Use $conference-logo-maintainer to update the CCF conference logo assets.

Please complete the whole workflow automatically:
- refresh or repair conference logos;
- apply manual correction records;
- keep hard-to-resolve logo entries blank when required;
- flag year/city/venue-sensitive logos;
- flag white or transparent logos;
- sync the final assets to Better-Poster-Skill if available;
- report the final asset count, skipped entries, validation result, and remaining manual-review items.
```

agent 会根据 skill 内部说明完成维护，并汇报最终结果。

### Master Prompt

需要完整一键维护时，可以直接复制下面的 Prompt 给 code agent：

```text
You are maintaining the Conference Logo Maintainer Skill.

Goal:
Update the CCF conference logo assets end to end and produce a final, validated asset set.

Requirements:
1. Refresh CCF A/B/C conference logo assets using the existing Conference Logo Maintainer Skill logic.
2. Preserve confirmed good existing logos unless a better official source is found.
3. Apply manual correction records:
   - Conferences absent from manual corrections must continue through the normal automated tracking flow.
   - Conferences marked as having an exact logo must use the configured official logo URL or yearly URL template first.
   - Conferences marked as having only a website and no reliable logo must remain blank and must not be crawled.
4. Detect and avoid false positives such as speaker portraits, venue photos, sponsor marks, society logos, UI icons, and unrelated acronym matches.
5. Identify logos that should be prioritized for future yearly refresh because they contain year, city, or venue signals.
6. Identify white or transparent logos that may be invisible on white backgrounds and report them clearly.
7. Sync the final logo assets into the downstream project logo directory if one is present.
8. Validate that the maintained logo directory and downstream copy have matching file names and hashes.

Deliverables:
- Updated logo assets.
- Updated machine-readable manifest.
- Updated human-readable maintenance checklist.
- Updated yearly-refresh and white-logo watchlist report.
- Final summary with processed count, asset count, skipped/blank conferences, validation result, and any remaining manual review items.
```

### 输出什么

根据工作区状态和网络可用性，agent 可以返回：

- 更新后的会议 Logo 文件。
- 机器可读的 Logo manifest。
- 人工可读的维护清单。
- 年度更新优先级报告。
- 白色 Logo 视觉检查提醒清单。
- 简短的资产更新数量、留空条目、验证状态和剩余人工检查项说明。

### 人工检查

在将 Logo 用于海报、网站或重新分发前，请人工确认：

| 检查项 | 原因 |
|---|---|
| Logo 身份 | 资产应对应目标会议，而不是组织、赞助商、演讲者或会场。 |
| 年份、城市和地点文字 | 年度会议 Logo 很容易随年份变旧。 |
| 背景可见性 | 白色或透明 Logo 在白底海报或网页中可能不可见。 |
| 商标和版权 | 会议品牌材料可能有重新分发或署名要求。 |
| 下游渲染效果 | 请始终检查最终海报、网页或资产包中的实际显示效果。 |

### License

This repository is MIT licensed.

重新分发生成或下载的会议 Logo 文件前，请检查对应会议的版权、商标和署名要求。

<p align="right"><a href="#conference-logo-maintainer-skill">Back to top</a> · <a href="#english">English</a></p>
