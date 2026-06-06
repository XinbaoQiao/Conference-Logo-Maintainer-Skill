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
| ICWS | ICWSM.jpg / ICWS.png | 无 | no_logo_candidate | https://services.conferences.computer.org/2026/icws-2026/ | 视觉复核发现 ICWS.png 是 IEEE SERVICES 会议群标识，非 ICWS 专属 Logo，已删除。 |
| SoCC | Cloud.png | SoCC.png | downloaded | https://acmsocc.org/2026/assets/img/socc-logo.png | 官方页列表缺少 ACM SoCC 标识，通过页面直接发现 socc-logo.png。 |
| CP | CP.jpg | CP.png | downloaded | https://cp2026.a4cp.org/images/logos/cp2026_belem_logo_300x300.png | 原图来自 unsplash 个人头像风景照。 |
| IJCNN | IJCNN.jpg | IJCNN.webp | downloaded | https://confcats-siteplex.s3.amazonaws.com/ijcnn/glide-cache/containers/logos/ijcnn27-logo-hr_color-simple.webp/e36784d58dd02682aca1842b8374b346/ijcnn27-logo-hr_color-simple.webp | 官方页候选为 OpenAI 水印图，改取 IJCNN 官方站点 logo。 |
| ASSETS | ASSETS.png | ASSETS.svg | downloaded | https://assets25.sigaccess.org/favicon.svg | 原文件为人物头像，改用 ASSETS 官方会议站点 favicon。 |

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

## 视觉复核追加清理

本轮补做了 125 个大图/长图/来源可疑候选的缩略图视觉复核，并在清理后扩展复看 91 个长图/大图候选；白色透明 Logo 已用深色背景复核，确认以下额外误收集资产。

| 会议 | 原文件 | 原因 | 当前状态 |
| --- | --- | --- | --- |
| ADMA | ADMA.jpg | 城市夜景照片，非会议 Logo。 | no_logo_candidate |
| AFT | AFT.jpg | 伦敦大本钟照片，非会议 Logo。 | no_logo_candidate |
| CAV | CAV.jpg | 里斯本景点照片，非会议 Logo。 | no_logo_candidate |
| CLUSTER | CLUSTER.jpg | IEEE 组织 Logo，非 CLUSTER 会议 Logo。 | no_logo_candidate |
| COCOON | COCOON.jpg | 新加坡城市照片，非会议 Logo。 | no_logo_candidate |
| CSFW | CSFW.png | IEEE Computer Society 组织 Logo，非 CSFW 会议 Logo。 | no_logo_candidate |
| DFRWS APAC | DFRWS APAC.jpg | 城市/日落照片，非 DFRWS APAC 会议 Logo。 | no_logo_candidate |
| EASE | EASE.jpg | TCS 赞助商 Logo，非 EASE 会议 Logo。 | no_logo_candidate |
| EuroVis | EuroVis.jpg | 地图截图，非 EuroVis 会议 Logo。 | no_logo_candidate |
| FC | FC.png | IFCA/Foundation 组织标识，非 FC 会议专属 Logo。 | no_logo_candidate |
| FG | FG.webp | IEEE Computer Society 组织 Logo，非 FG 会议 Logo。 | no_logo_candidate |
| FPGA | FPGA.jpg | 颁奖/合影照片，非 FPGA 会议 Logo。 | no_logo_candidate |
| GLSVLSI | GLSVLSI.jpg | 多张场地照片拼图，非 GLSVLSI 会议 Logo。 | no_logo_candidate |
| HotOS | HotOS.png | ACM 组织 Logo，非 HotOS 会议 Logo。 | no_logo_candidate |
| HPDC | HPDC.jpg | 校园照片，非 HPDC 会议 Logo。 | no_logo_candidate |
| HSCC | HSCC.png | Vanderbilt University 校徽/字标，非 HSCC 会议 Logo。 | no_logo_candidate |
| ICA3PP | ICA3PP.jpg | 城市夜景照片，非 ICA3PP 会议 Logo。 | no_logo_candidate |
| ICDCS | ICDCS.jpg | 宫殿/景点照片，非 ICDCS 会议 Logo。 | no_logo_candidate |
| ICFP | ICFP.jpg | 城市照片，非 ICFP 会议 Logo。 | no_logo_candidate |
| ICMR | ICMR.png | ACM 组织圆标，非 ICMR 会议 Logo。 | no_logo_candidate |
| ICPP | ICPP.webp | 新加坡城市照片，非 ICPP 会议 Logo。 | no_logo_candidate |
| ICSME | ICSME.jpg | 建筑/景点照片，非 ICSME 会议 Logo。 | no_logo_candidate |
| ICWS | ICWS.png | IEEE SERVICES 会议群标识，非 ICWS 专属 Logo。 | no_logo_candidate |
| ICWSM | ICWSM.jpg | 城市日落照片，非 ICWSM 会议 Logo。 | no_logo_candidate |
| IJCB | IJCB.jpg | 罗马景点照片，非 IJCB 会议 Logo。 | no_logo_candidate |
| INSCRYPT | INSCRYPT.jpg | 香港城市照片，非 INSCRYPT 会议 Logo。 | no_logo_candidate |
| Internetware | Internetware.png | 海岸/城市照片，非 Internetware 会议 Logo。 | no_logo_candidate |
| ISSTA | ISSTA.jpg | AWS 赞助商 Logo，非 ISSTA 会议 Logo。 | no_logo_candidate |
| IWQoS | IWQoS.webp | 安全/科技素材图，非 IWQoS 会议 Logo。 | no_logo_candidate |
| LCN | LCN.jpg | 校园/建筑照片，非 LCN 会议 Logo。 | no_logo_candidate |
| LCTES | LCTES.jpg | 城市运河照片，非 LCTES 会议 Logo。 | no_logo_candidate |
| MSWiM | MSWiM.webp | 桥梁/夜景照片，非 MSWiM 会议 Logo。 | no_logo_candidate |
| OOPSLA | OOPSLA.jpg | 城市天际线照片，非 OOPSLA 会议 Logo。 | no_logo_candidate |
| POPL | POPL.png | ACM SIGPLAN 组织 Logo，非 POPL 会议 Logo。 | no_logo_candidate |
| PPoPP | PPoPP.png | 会议日程截图，非 PPoPP 会议 Logo。 | no_logo_candidate |
| RTAS | RTAS.png | IEEE Computer Society 组织 Logo，非 RTAS 会议 Logo。 | no_logo_candidate |
| RTSS | RTSS.png | 城市夜景照片，非 RTSS 会议 Logo。 | no_logo_candidate |
| SACMAT | SACMAT.jpg | LinkedIn 图标，非 SACMAT 会议 Logo。 | no_logo_candidate |
| SAS | SAS.jpg | 新加坡城市夜景照片，非 SAS 会议 Logo。 | no_logo_candidate |
| SLT | SLT.png | IEEE Signal Processing Society 组织 Logo，非 SLT 会议 Logo。 | no_logo_candidate |
| SPAA | SPAA.jpg | 建筑/校园照片，非 SPAA 会议 Logo。 | no_logo_candidate |
| TrustCom | TrustCom.jpg | 二维码/票据截图，非 TrustCom 会议 Logo。 | no_logo_candidate |
| VEE | VEE.png | Huawei 赞助商/厂商 Logo，非 VEE 会议 Logo。 | no_logo_candidate |
| ATVA | ATVA.jpg | IIT Bombay 机构 Logo，非 ATVA 会议 Logo。 | no_logo_candidate |
| APLAS | APLAS.png | Microsoft 公司 Logo，非 APLAS 会议 Logo。 | no_logo_candidate |
| ASE | ASE.png | 城市/场地照片，未含 ASE 会议标识。 | no_logo_candidate |
| CVM | CVM.png | Computational Visual Media 出版社/IEEE Xplore 图，非 CVM 会议 Logo。 | no_logo_candidate |
| ISAAC | ISAAC.jpg | 水墨景观背景图，未含 ISAAC 会议标识。 | no_logo_candidate |
| PG | PG.jpg | 图形渲染/城市主视觉背景，未含 PG 会议标识。 | no_logo_candidate |
| SSE | SSE.png | University of Helsinki 机构 Logo，非 SSE 会议 Logo。 | no_logo_candidate |

## 本轮清理后完整性复核

- 重新运行 `python scripts/audit_logo_integrity.py --manifest manifest.json --overrides audit/false_positive_overrides.json`：
- `Confirmed bad mappings still present`: `_None._`
- `Shared logo-file warnings`: `_None._`
- `Duplicate content-hash warnings`: `_None._`
- `Suspicious source-url warnings`: `_None._`
- `Acronym/generic-stem warnings`: 仍剩 `Cloud`（由 `Cloud` 独占）。
- 追加语义与视觉可疑项扫描后，已移除人脸图、城市/建筑照片、赞助商/组织 logo、二维码/日程截图等误收集资产。

## 仍需手工复核/告警（爬虫优化）

1. `DFRWS`: 当前仍为 `no_logo_candidate`，原因是页面候选缺少稳定高清通用图标。
2. 允许 `annual` 标记存在于含年份官方页面的 no-logo 记录（如 `ICIC`、`AsiaCCS`、`BlockSys`）；这些需要官方新页后再次补抓。

## 规则建议（后续爬取优化）

- 将 `audit/false_positive_overrides.json` 的 `confirmed_bad_mappings` 作为 `existing_logo_index` 前置过滤。
- 复用时限制 title 匹配边界：禁止 `ICWS` 命中 `ICWSM`、`ICIC` 命中 `ICICS`、`SoCC` 命中 `Cloud`。
- 对明显社交/头像/无关内容（`unsplash`, `Photo`, `portrait`, `favicon`）设置更高拒分。
- 增加内容 hash 重复检查：同一二进制图片被多个不同会议使用时，除明确联合会议外应进入人工复核。
- 对组织/赞助商通用 logo（例如 IACR wordmark、sponsor logo）设置拒分，除非 manifest 明确标注为会议官方主视觉。
