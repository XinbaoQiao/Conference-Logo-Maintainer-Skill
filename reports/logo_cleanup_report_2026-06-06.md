# 会议 Logo 全量清理与复核报告（2026-06-06）

生成时间: 2026-06-06
仓库: `https://github.com/XinbaoQiao/Conference-Logo-Maintainer-Skill`

## 目标与方法

- 通过 `scripts/audit_logo_integrity.py` 进行全量条目扫描（314 条会议），并追加源 URL/尺寸/内容 hash 可疑项扫描。
- 结合页面候选重抓（`fetch_ccf_logos.py`）对高风险条目逐一核验候选源。
- 对确认错误的映射执行剔除/替换，并更新 `manifest.json` 与 `update_list.md`。

## 已清洗/替换清单

| 会议 | 旧文件 | 新文件 | 状态 | 替换来源 | 变更说明 |
| --- | --- | --- | --- | --- | --- |
| ICWS | ICWSM.jpg | ICWS.png | downloaded | https://services.conferences.computer.org/2025/wp-content/uploads/sites/3/2024/10/logo-icws-new.png | 官方链接 2026 页面 404，用 2025 官方页确认为 ICWS 标识。 |
| SoCC | Cloud.png | SoCC.png | downloaded | https://acmsocc.org/2026/assets/img/socc-logo.png | 官方页列表缺少 ACM SoCC 标识，通过页面直接发现 socc-logo.png。 |
| CP | CP.jpg | CP.png | downloaded | https://cp2026.a4cp.org/images/logos/cp2026_belem_logo_300x300.png | 原图来自 unsplash 个人头像风景照。 |
| IJCNN | IJCNN.jpg | IJCNN.webp | downloaded | https://confcats-siteplex.s3.amazonaws.com/ijcnn/glide-cache/containers/logos/ijcnn27-logo-hr_color-simple.webp/e36784d58dd02682aca1842b8374b346/ijcnn27-logo-hr_color-simple.webp | 官方页候选为 OpenAI 水印图，改取 IJCNN 官方站点 logo。 |

## 标记为 no_logo_candidate 的条目

| 会议 | 原文件 | 原因 | 当前状态 |
| --- | --- | --- | --- |
| CoNLL | CoNLL.jpg | exif 为人物画像/会议介绍无关图 | no_logo_candidate |
| SAT | SAT.jpg | logo 候选为 AI Journal，页面无明确会议 logo | no_logo_candidate |
| ICIC | ICICS.png | 页面超时/仅返回边界性图片，未检出会议主标 | no_logo_candidate |
| AsiaCCS | CCS.png | 页面仅 ACM/SIGSAC/社交图标，无专属 AsiaCCS 标识 | no_logo_candidate |
| BlockSys | BlockSys.jpg | 候选为 CCIS-Logo 与 2 列图像片段，非会议独立 Logo | no_logo_candidate |
| DFRWS | DFRWS APAC.jpg | 可能复用 APAC 版式，EU 版未检出明确可复用 logo，先标记为待确认缺失 | no_logo_candidate |
| ISPA | ISPA.jpg | 官方候选 cropped-ny1.jpg 是纽约/页面头图，非会议 Logo。 | no_logo_candidate |
| CODASPY | CODASPY.png | 源图为 Secunet Security Networks 赞助商 Logo，非 CODASPY 会议 Logo。 | no_logo_candidate |
| ASIACRYPT | ASIACRYPT.png | 同一 IACR 组织 wordmark 被复用于多个会议，非 ASIACRYPT 专属 Logo。 | no_logo_candidate |
| CHES | CHES.png | 同一 IACR 组织 wordmark 被复用于多个会议，非 CHES 专属 Logo。 | no_logo_candidate |
| CRYPTO | CRYPTO.png | 同一 IACR 组织 wordmark 被复用于多个会议，非 CRYPTO 专属 Logo。 | no_logo_candidate |
| FSE (SC) | FSE-SC.png | 同一 IACR 组织 wordmark 被复用于多个会议，非 FSE 专属 Logo。 | no_logo_candidate |
| TCC | TCC.png | 同一 IACR 组织 wordmark 被复用于多个会议，非 TCC 专属 Logo。 | no_logo_candidate |
| PODC | PODC.jpg | 残留图片带 Nikon 相机 EXIF，官方页面未确认会议主 Logo，判定为照片/横幅误收集。 | no_logo_candidate |

## 本轮清理后完整性复核

- 重新运行 `python scripts/audit_logo_integrity.py --manifest manifest.json --overrides audit/false_positive_overrides.json`：
- `Confirmed bad mappings still present`: `_None._`
- `Shared logo-file warnings`: `_None._`
- `Duplicate content-hash warnings`: `_None._`
- `Suspicious source-url warnings`: `_None._`
- `Acronym/generic-stem warnings`: 仍剩 `Cloud`（由 `Cloud` 独占）。
- 追加语义可疑项扫描后，已移除 ISPA 页面头图、CODASPY 赞助商 logo、5 个 IACR 组织 wordmark 复用，并移除 PODC 相机照片型资产。

## 仍需手工复核/告警（爬虫优化）

1. `DFRWS`: 当前仍为 `no_logo_candidate`，原因是页面候选缺少稳定高清通用图标。
2. 允许 `annual` 标记存在于含年份官方页面的 no-logo 记录（如 `ICIC`、`AsiaCCS`、`BlockSys`）；这些需要官方新页后再次补抓。

## 规则建议（后续爬取优化）

- 将 `audit/false_positive_overrides.json` 的 `confirmed_bad_mappings` 作为 `existing_logo_index` 前置过滤。
- 复用时限制 title 匹配边界：禁止 `ICWS` 命中 `ICWSM`、`ICIC` 命中 `ICICS`、`SoCC` 命中 `Cloud`。
- 对明显社交/头像/无关内容（`unsplash`, `Photo`, `portrait`, `favicon`）设置更高拒分。
- 增加内容 hash 重复检查：同一二进制图片被多个不同会议使用时，除明确联合会议外应进入人工复核。
- 对组织/赞助商通用 logo（例如 IACR wordmark、sponsor logo）设置拒分，除非 manifest 明确标注为会议官方主视觉。
