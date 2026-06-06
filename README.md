# Conference Logo Maintainer Skill

[English](#english) | [中文](#zh-cn)

<a id="english"></a>

## English

Conference Logo Maintainer Skill helps a code agent maintain CCF conference logo assets in one shot.

Use it when you want an agent to refresh, repair, audit, and sync conference logos without manually crawling conference websites or running maintenance commands yourself.

### What This Project Provides

- A maintained CCF A/B/C conference logo asset set.
- Automatic discovery of current official conference logos when reliable sources are available.
- Manual correction support for conferences with confirmed logo URLs or intentionally blank logo entries.
- Year, city, and venue-sensitive logo tracking for future refreshes.
- White or transparent logo warnings for visual QA on white backgrounds.
- Machine-readable and human-readable reports for downstream use.
- Optional synchronization into Better-Poster-Skill when both projects exist in the same workspace.

### How To Use

Install this repository as a Codex skill, then ask the code agent to update the conference logo assets.

```bash
mkdir -p ~/.codex/skills
cp -R Conference-Logo-Maintainer-Skill ~/.codex/skills/conference-logo-maintainer
```

Example request:

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

Depending on the workspace and available network access, the agent can return:

- Updated logo files.
- A machine-readable logo manifest.
- A human-readable maintenance checklist.
- A yearly-refresh priority report.
- A white-logo visual QA watchlist.
- A short summary of updated assets, intentionally blank entries, validation status, and remaining manual checks.

### User Check

Before using the logos in posters, websites, or redistributed assets, manually verify:

- Logo identity and conference relevance.
- Year, city, and venue correctness.
- Visibility on the intended background color.
- Trademark, copyright, and attribution requirements.

AI-assisted logo maintenance can reduce manual crawling, but final branding judgment remains with the user.

### License

This repository is MIT licensed.

Review conference logo copyright, trademark, and attribution requirements before redistributing generated or downloaded logo files.

[中文](#zh-cn)

---

<a id="zh-cn"></a>

## 中文

Conference Logo Maintainer Skill 用于帮助 code agent 一次性维护 CCF 会议 Logo 资产。

当你希望自动刷新、修复、审计并同步 CCF 会议 Logo，而不想手动访问大量会议官网、手动运行爬虫或维护命令时，可以使用这个项目。

### 这个项目提供什么

- 一套持续维护的 CCF A/B/C 会议 Logo 资产。
- 在可靠来源存在时，自动查找当前官方会议 Logo。
- 支持手工修正记录：包括已确认 Logo URL 的会议，以及应当留空、不再抓取的会议。
- 标记带有年份、城市、地点信息的 Logo，方便后续年度更新。
- 标记白色或透明 Logo，提醒在白底场景中可能不可见。
- 生成机器可读和人工可读的维护结果，方便下游项目使用。
- 当同一工作区中存在 Better-Poster-Skill 时，可自动同步最终 Logo 资产。

### 怎么使用

先把本仓库安装为 Codex skill，然后让 code agent 自动完成会议 Logo 更新。

```bash
mkdir -p ~/.codex/skills
cp -R Conference-Logo-Maintainer-Skill ~/.codex/skills/conference-logo-maintainer
```

示例请求：

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

agent 会自动完成 Logo 更新、手工修正规则应用、误匹配排查、年度更新提醒、白色 Logo 提醒、下游同步和最终结果汇报。

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

- 更新后的 Logo 文件。
- 机器可读的 Logo manifest。
- 人工可读的维护清单。
- 年度更新优先级报告。
- 白色 Logo 视觉检查提醒清单。
- 简短的资产更新数量、留空条目、验证状态和剩余人工检查项说明。

### 人工检查

在将 Logo 用于海报、网站或重新分发前，请人工确认：

- Logo 是否确实对应目标会议。
- 年份、城市和地点信息是否正确。
- Logo 在目标背景色上是否可见。
- 是否满足会议 Logo 的版权、商标和署名要求。

AI 可以减少批量检索和维护成本，但最终品牌使用判断仍应由使用者完成。

### License

This repository is MIT licensed.

重新分发生成或下载的会议 Logo 文件前，请检查对应会议的版权、商标和署名要求。

[English](#english)
