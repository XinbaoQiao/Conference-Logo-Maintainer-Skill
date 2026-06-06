# 会议 Logo 全量视觉审计清单

审计日期：2026-06-06

> 说明：上一份报告只覆盖了 manifest 层面的“错误映射/跨会议复用”。这份清单扩大到视觉层面的高风险图片：可能混入人物照片、会场照片、网页截图、banner、hero 图、社交分享图、地区/年份专属图、组织 Logo 误替代会议 Logo 等。

## A. 已确认需要修正的错误映射

| 优先级 | 会议 | 当前文件 | 问题类型 | 处理建议 |
| --- | --- | --- | --- | --- |
| P0 | ICWS | `assets/logos/ICWSM.jpg` | 跨会议误复用：ICWS 被映射到 ICWSM | ICWS 改为 `no_logo_candidate`，重新从 ICWS 官方页确认后再收录 |
| P0 | AsiaCCS | `assets/logos/CCS.png` | 跨会议误复用：AsiaCCS 被映射到 ACM CCS | AsiaCCS 改为 `no_logo_candidate`，不得用 CCS/ACM/SIGSAC/social icon 代替 |
| P0 | SoCC | `assets/logos/Cloud.png` | 泛化词误复用：SoCC 因 cloud computing 描述命中 IEEE CLOUD | 替换为 SoCC 官方品牌图，候选：`https://acmsocc.org/2026/assets/img/logo.png` |
| P0 | ICIC | `assets/logos/ICICS.png` | 短缩写误复用：ICIC 被映射到 ICICS | ICIC 改为 `no_logo_candidate`，重新从 ICIC 官方页确认 |
| P1 | DFRWS | `assets/logos/DFRWS APAC.jpg` | 区域/年份专属图疑似复用到 DFRWS EU | 若图片含 APAC/2025 字样，则 DFRWS EU 改为 `no_logo_candidate` 或另找通用 DFRWS Logo |

## B. 高风险：可能是人物照/会场照/网页截图/海报图的文件

筛选规则：`*.jpg`、`*.webp`、`*.gif` 优先，因为这些格式在会议官网中经常来自 speaker/photo/hero/banner/og:image，而不是干净 Logo。以下文件需要逐张视觉打开确认。

| 优先级 | 会议/文件 | 当前文件 | 风险原因 | 建议动作 |
| --- | --- | --- | --- | --- |
| P0 | ICWS | `ICWSM.jpg` | 已确认错配；可能不是 ICWS Logo | 从 ICWS 映射中删除 |
| P0 | SoCC | `Cloud.png` | 已确认错配；泛名文件 | 从 SoCC 映射中删除并替换官方 SoCC 图 |
| P0 | AsiaCCS | `CCS.png` | 已确认错配；组织/其他会议 Logo | 从 AsiaCCS 映射中删除 |
| P0 | ICIC | `ICICS.png` | 已确认错配 | 从 ICIC 映射中删除 |
| P1 | CAV | `CAV.jpg` | JPG，高风险自然图/会场图/海报图 | 视觉确认；不是纯会议 Logo 则替换 |
| P1 | CSCW | `CSCW.webp` | WEBP，高风险网页 hero/social 图 | 视觉确认；不是纯会议 Logo 则替换 |
| P1 | DAC | `DAC.webp` | WEBP，高风险网页 banner/social 图 | 视觉确认；不是纯会议 Logo 则替换 |
| P1 | FOCS | `FOCS.gif` | GIF，可能为低质旧网页图 | 视觉确认；优先替换 SVG/PNG |
| P1 | HPDC | `HPDC.jpg` | JPG，高风险自然图/海报图 | 视觉确认 |
| P1 | IEEE VR | `IEEE VR.webp` | WEBP，高风险网页图 | 视觉确认 |
| P1 | ISSTA | `ISSTA.jpg` | JPG，researchr 页面常见 banner/track 图 | 视觉确认 |
| P1 | OOPSLA | `OOPSLA.jpg` | JPG，researchr/SPLASH 轨道图风险 | 视觉确认 |
| P1 | SIGOPS ATC | `SIGOPS ATC.jpg` | JPG，高风险网页图 | 视觉确认 |
| P1 | WWW | `WWW.jpg` | JPG，高风险网页图 | 视觉确认 |
| P1 | CLUSTER | `CLUSTER.jpg` | JPG，高风险自然图/会场图 | 视觉确认 |
| P1 | COCOON | `COCOON.jpg` | JPG，高风险自然图/海报图 | 视觉确认 |
| P1 | CONCUR | `CONCUR.webp` | WEBP，高风险网页图 | 视觉确认 |
| P1 | CP | `CP.jpg` | JPG，高风险自然图/海报图 | 视觉确认 |
| P1 | ECML-PKDD | `ECML-PKDD.jpg` | JPG，高风险 banner/og:image | 视觉确认 |
| P1 | ESEM | `ESEM.jpg` | JPG，researchr 页面轨道图风险 | 视觉确认 |
| P1 | ETAPS | `ETAPS.webp` | WEBP，高风险网页图 | 视觉确认 |
| P1 | ICCBR | `ICCBR.jpg` | JPG，高风险自然图/海报图 | 视觉确认 |
| P1 | ICDCS | `ICDCS.jpg` | JPG，高风险网页图 | 视觉确认 |
| P1 | IPDPS | `IPDPS.jpg` | JPG，高风险网页图 | 视觉确认 |
| P1 | ISMAR | `ISMAR.gif` | GIF，可能为低质/动画旧图 | 视觉确认，优先替换静态高清图 |
| P1 | LCTES | `LCTES.jpg` | JPG，researchr 页面轨道图风险 | 视觉确认 |
| P1 | MobiHoc | `MobiHoc.jpg` | JPG，高风险自然图/会场图 | 视觉确认 |
| P1 | PG | `PG.jpg` | JPG，高风险自然图/海报图 | 视觉确认 |
| P1 | PKC | `PKC.jpg` | JPG，高风险自然图/海报图 | 视觉确认 |
| P1 | PODC | `PODC.jpg` | JPG，高风险旧网页图 | 视觉确认 |
| P1 | RAID | `RAID.webp` | WEBP，高风险网页图 | 视觉确认 |
| P1 | RE | `RE.jpg` | JPG，researchr 页面轨道图风险 | 视觉确认 |
| P1 | SAS | `SAS.jpg` | JPG，researchr/SPLASH 轨道图风险 | 视觉确认 |
| P1 | SECON | `SECON.webp` | WEBP，高风险网页图 | 视觉确认 |
| P1 | SIGMETRICS | `SIGMETRICS.jpg` | JPG，高风险网页图 | 视觉确认 |
| P1 | VMCAI | `VMCAI.jpg` | JPG，高风险网页图 | 视觉确认 |
| P1 | WSDM | `WSDM.jpg` | JPG，高风险网页图 | 视觉确认 |
| P1 | ACISP | `ACISP.jpg` | JPG，高风险会议网页/hero 图 | 视觉确认 |
| P1 | ACNS | `ACNS.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | ADMA | `ADMA.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | ATVA | `ATVA.jpg` | JPG，researchr 页面轨道图风险 | 视觉确认 |
| P1 | BlockSys | `BlockSys.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | CASA | `CASA.jpg` | JPG，sciencesconf 页面常见照片/横幅风险 | 视觉确认；若为人物/会场图则删除 |
| P1 | DAI | `DAI.webp` | WEBP，高风险网页图 | 视觉确认 |
| P1 | DFRWS / DFRWS APAC | `DFRWS APAC.jpg` | 共享且可能为 APAC 专属图 | 拆分或重命名通用图 |
| P1 | EASE | `EASE.jpg` | JPG，researchr 页面轨道图风险 | 视觉确认 |
| P1 | ETS | `ETS.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | FG | `FG.webp` | WEBP，可能是人物/人脸/会议海报图 | 视觉确认；若为人物照必须删除 |
| P1 | FPT | `FPT.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | GLOBECOM | `GLOBECOM.webp` | WEBP，高风险网页 banner/social 图 | 视觉确认 |
| P1 | HPCC | `HPCC.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | HotNets | `HotNets.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | ICA3PP | `ICA3PP.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | ICFEM | `ICFEM.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | IJCB | `IJCB.jpg` | JPG，biometrics 会议，可能出现人脸/person/hero 图 | 视觉确认；若为人物/人脸图必须删除 |
| P1 | IJCNN | `IJCNN.jpg` | JPG，高风险 WCCI 页面图 | 视觉确认 |
| P1 | INSCRYPT | `INSCRYPT.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | ISAAC | `ISAAC.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | ISPA | `ISPA.jpg` | JPG，旧 cloud-conf 页面，高风险网页图/非 Logo | 视觉确认；若是人物/会场/背景图则删除 |
| P1 | MSWiM | `MSWiM.webp` | WEBP，高风险网页图 | 视觉确认 |
| P1 | Networking | `Networking.jpg` | JPG，高风险会议照片/hero 图 | 视觉确认 |
| P1 | NSPW | `NSPW.jpg` | JPG，高风险网页图 | 视觉确认 |
| P1 | PRICAI | `PRICAI.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | REFSQ | `REFSQ.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | SACMAT | `SACMAT.jpg` | JPG，高风险会议网页图 | 视觉确认 |
| P1 | TrustCom | `TrustCom.jpg` | JPG，高风险复合会议网页图 | 视觉确认 |
| P1 | WCNC | `WCNC.webp` | WEBP，高风险网页图 | 视觉确认 |
| P1 | WISA | `WISA.jpg` | JPG，高风险会议网页图 | 视觉确认 |

## C. 泛名/共享文件名风险

| 文件 | 当前风险 | 建议 |
| --- | --- | --- |
| `Cloud.png` | 泛名文件，已误用于 SoCC；还可能误用于其他 cloud computing 会议 | 禁止 description 词触发复用；只允许 title/DBLP 精确命中 |
| `CCS.png` | 同时被 AsiaCCS 误用；短缩写包含关系风险 | 对短 acronym 使用 token/边界匹配 |
| `ICWSM.jpg` | 被 ICWS 误用 | 短 acronym 不能用 prefix 匹配 |
| `ICICS.png` | 被 ICIC 误用 | 短 acronym 不能用 prefix 匹配 |
| `DFRWS APAC.jpg` | 区域会议图可能被主会议误用 | 若非通用标识，应按地区/年份拆分 |
| `ICML-logo.svg` | 文件名含 `logo`，但整体可接受；低风险 | 保留，但无需列入误配 |

## D. 下一步清洗策略

1. 先处理 A 类 P0：从 manifest/update_list 逻辑上移除错误映射，不删除仍属于原会议的文件。
2. 对 B 类逐张打开图片，凡出现以下任一情况直接剔除：
   - 人像、头像、speaker 照片、合照、会场照片；
   - venue/city 景观图；
   - 网页整页截图、hero/banner 背景图；
   - sponsor/partner/exhibitor/organization logo，而不是会议本身 Logo；
   - 年份或地区专属图被复用到另一会议/年份。
3. 正确替换优先级：SVG > 透明 PNG > 高清官方 PNG/JPG；不要用 favicon、社交分享图、OpenGraph 大图、网页背景图。
4. 清洗后重新生成 `manifest.json` 和 `update_list.md`，再运行 `scripts/audit_logo_integrity.py`。
