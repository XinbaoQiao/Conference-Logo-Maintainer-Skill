# 会议 Logo 数据审计与清理预警报告

审计日期：2026-06-06

审计对象：`manifest.json`、`update_list.md`、`assets/logos/*` 的当前映射关系，以及部分被判定为高风险的官方会议页面。

## 执行结论

本次审计发现 4 个高置信度错误映射，均属于“现有本地图片被错误复用到相似会议名/相似描述”的问题；另发现 1 个需要人工视觉复核的区域性 Logo 复用风险。

已提交的清理工件：

- `audit/false_positive_overrides.json`：机器可读的错误映射覆盖清单，用于阻止后续爬虫继续静默复用错误 Logo。
- `scripts/audit_logo_integrity.py`：可重复运行的完整性审计脚本，用于发现已确认错误、重复 logo_file、缩写/文件名不匹配、泛化文件名误用等风险。
- `reports/logo_audit_2026-06-06.md`：本报告。

## 已确认错误与清洗建议

| 错误图片路径/会议 | 当前错误映射 | 错误原因 | 替换/清洗状态 | 后续动作 |
| --- | --- | --- | --- | --- |
| `assets/logos/ICWSM.jpg` / ICWS | ICWS 被映射到 `ICWSM.jpg` | ICWS 与 ICWSM 是不同会议；当前规则允许相似缩写或描述导致跨会议复用 | 未写入替换二进制；应把 ICWS 从该图片映射中剔除并转为 `no_logo_candidate` | 重新从 `https://services.conferences.computer.org/2026/icws-2026/` 抓取，经人工确认后再恢复 `logo_file` |
| `assets/logos/CCS.png` / AsiaCCS | AsiaCCS 被映射到 `CCS.png` | AsiaCCS 与 ACM CCS 不同；2027 AsiaCCS 页面暴露的是 ACM/SIGSAC/社交图标类资源，未确认独立 AsiaCCS Logo | 不应以 `CCS.png`、ACM、SIGSAC 或社交图标替代；推荐 `no_logo_candidate` | 等官方页面提供明确 AsiaCCS Logo 后再收录 |
| `assets/logos/Cloud.png` / SoCC | SoCC 被映射到 `Cloud.png` | SoCC 描述含 cloud computing，命中了 IEEE CLOUD 的本地资产；属于描述词触发的跨会议复用 | 官方 SoCC 2026 品牌图确认在 `https://acmsocc.org/2026/assets/img/logo.png`；本次未写入外部二进制 | 下一轮下载该官方资产并命名为 `SoCC.png` 或 `SoCC.svg`，再更新 manifest |
| `assets/logos/ICICS.png` / ICIC | ICIC 被映射到 `ICICS.png` | ICIC 与 ICICS 仅差尾部 `S`，但属于不同会议；当前缩写匹配过宽 | 未写入替换二进制；应把 ICIC 从 `ICICS.png` 映射中剔除并转为 `no_logo_candidate` | 从 `https://www.ic-icc.cn/2026/` 重新确认；无法访问或无明确 Logo 时保持人工检查 |

## 高风险人工复核项

| 图片路径/会议 | 风险原因 | 建议 |
| --- | --- | --- |
| `assets/logos/DFRWS APAC.jpg` / DFRWS | DFRWS EU 2026 与 DFRWS APAC 2025 共享 `DFRWS APAC.jpg`。如果该图片包含 APAC 年会/地区标识，则不应给 DFRWS EU 使用。 | 人工视觉检查；若为通用 DFRWS 标识，建议改名为通用 `DFRWS.*`；若为 APAC 专属图，应将 DFRWS EU 2026 标为 `no_logo_candidate`。 |

## 爬虫逻辑异常预警

### 1. `find_existing_logo()` 的本地复用匹配过宽

当前复用逻辑会在未开启 `--refresh-existing` 时优先复用本地文件。如果本地文件 stem 与 title、alias、description 存在宽松匹配，就可能跳过官方页面重新抓取。

已暴露问题：

- `ICWS` 复用 `ICWSM.jpg`
- `ICIC` 复用 `ICICS.png`
- `SoCC` 复用 `Cloud.png`
- `AsiaCCS` 复用 `CCS.png`

建议：

- acronym 类会议名必须做边界匹配，不能允许 `ICWS` 命中 `ICWSM`、`ICIC` 命中 `ICICS`、`CCS` 命中 `AsiaCCS`。
- description 中的泛化词不得单独触发本地复用，例如 `cloud`、`security`、`web`、`systems`、`computing`。
- 对 duplicate/shared title 或短缩写会议，若本地 logo stem 与 title 非完全匹配，应强制进入 `--refresh-existing` 或 manual-check。

### 2. 需要把 false-positive override 前置到复用阶段

`audit/false_positive_overrides.json` 应在 `existing_logo_index()` / `find_existing_logo()` 之前加载。若当前 `(source_path, title, logo_file)` 出现在 confirmed bad mappings 中，则该本地文件不能作为复用候选。

建议伪逻辑：

```python
if is_blocked_logo_mapping(source_path, title, candidate_path.name):
    continue
```

### 3. 官方候选图筛选需要区分会议 Logo 与组织/社交/UI 图标

AsiaCCS 页面提供的 ACM、SIGSAC、Twitter/X 等图片不能替代会议 Logo。建议将以下类别直接降权或拒绝：

- `twitter`、`x-logo`、`facebook`、`linkedin`、`social`
- `acm`、`sig`、`sigsac`，除非 title 本身就是该组织会议且页面上下文明确
- `favicon`、`apple-touch-icon`、`menu`、`close`、`search`

### 4. 共享 logo_file 应触发强制预警

多个不同会议标题共享同一 `logo_file` 时，不应直接视为成功。共享文件可能合法，例如 umbrella event 或 joint conference，但必须显式列入 allowlist。

本次 confirmed 或 high-risk 共享包括：

- `ICWSM.jpg`：ICWS / ICWSM
- `ICICS.png`：ICIC / ICICS
- `Cloud.png`：Cloud / SoCC
- `CCS.png`：CCS / AsiaCCS
- `DFRWS APAC.jpg`：DFRWS / DFRWS APAC

## 建议运行方式

```bash
python scripts/audit_logo_integrity.py \
  --manifest manifest.json \
  --overrides audit/false_positive_overrides.json \
  --report reports/logo_integrity_check.md
```

如果 `Confirmed bad mappings still present` 非空，CI 应失败或至少阻止自动发布到 `Better-Poster-Skill/assets/logos`。

## 替换确认状态说明

- 已确认官方替换源但未写入二进制：SoCC，官方图片路径为 `https://acmsocc.org/2026/assets/img/logo.png`。
- 已确认不应继续复用旧图，但未确认官方替换图：ICWS、AsiaCCS、ICIC。
- 需人工视觉复核后决定是否重命名或拆分：DFRWS。

## 本次未直接删除的文件

未删除 `ICWSM.jpg`、`CCS.png`、`Cloud.png`、`ICICS.png`，因为这些文件分别仍可能是 ICWSM、CCS、Cloud、ICICS 自身的有效 Logo。清洗动作应针对错误映射关系，而不是无条件删除资产文件。
