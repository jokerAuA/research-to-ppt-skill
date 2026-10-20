---
name: research-to-ppt
description: 完整执行「主题调研 → 资料搜索与归档 → 论文资产（figures/tables）提取 → 用户选模板 → 尽量复用归档资产生成 PPT」的闭环工作流。当用户要求做一个基于调研的汇报/学术 PPT，或要求"先调研再出 PPT / 把资料做成可引用素材 / 搜索论文图片做进 PPT"时使用。触发词：调研+PPT、资料归档、论文图片提取、可引用素材、资产复用。
---

# 调研到 PPT 闭环工作流

一条流水线：**调研内容 → 搜索资料 → 把资料下载成可论文引用的 source（含
figures）→ 生成 PPT（先让用户选模板，尽可能多调用已归档资产）**。
四个阶段按序执行；每阶段完成后把产物落盘再进入下一阶段。

## 阶段总览

| 阶段 | 做什么 | 产物 | 细则 |
|---|---|---|---|
| A 调研 | 拆解主题、定信息需求 | 需求清单 | [research-archive.md §1](references/research-archive.md) |
| B 归档 | 搜索 + 精读 + 下载成可引用资产 | `资料归档\` + 总索引 | [research-archive.md §2-4](references/research-archive.md) |
| C 提取 | 论文 figures/tables 批量提取 + 分级 + token 映射 | `论文图片素材\` + manifest + 对照表 | [pdf-asset-extraction.md](references/pdf-asset-extraction.md) |
| D PPT | 先选模板 → 资产优先 → 逐页 lint/截图 → 双交付 | 在线 Slides + 本地 PPTX | [ppt-generation.md](references/ppt-generation.md) |

## 阶段 A · 调研内容

1. 完整理解用户主题，拆出：核心概念 / 关键案例 / 数据指标 / 争议与观点。
2. 明确交付物形态（PPT 页数倾向、受众、汇报场合），不确定时按合理默认推进，
   不反复打断用户。
3. 输出一份需求清单（可写进工作目录的调研笔记），后续每阶段对着它验收。

## 阶段 B · 搜索资料并归档为可引用 source

1. 按需并行搜索（通用/学术/垂直平台/搜图/视频），重要网页精读原文。
2. 关键数字必须记录来源（标题+URL+日期），禁止编造。
3. 建 `资料归档\` 目录（论文文献 / 网页文章 / 图片素材 / 视频链接），
   写《00-资料索引与备注.md》总索引，全部资产按 A/B/C 分级。
4. 论文 PDF 必须落到本地（这是阶段 C 的输入）。

## 阶段 C · 提取论文资产（figures / tables / sources）

1. 运行 `python scripts/extract_pdf_assets.py <pdf...> --out "资料归档/论文图片素材" --index`
   （阈值/倍率调参见 [pdf-asset-extraction.md §1](references/pdf-asset-extraction.md)）。
2. 逐张目检提取结果，按 A/B/C 分级，建立"图 → 论文页 → 用途"对照表。
3. 把要用的 A 级图上传到目标幻灯片，保存 `asset_tokens.json` 权威映射
   （图名 → file_token），后续补图直接复用。

## 阶段 D · 生成 PPT（先选模板，尽量多用资产）

1. **先询问模板偏好**（默认学术风格 / 简洁商务 / 用户自备模板 / 复刻样例），
   一次问清，选定后全程遵守。
2. 按 ppt skill 的编辑/新建流程逐页制作。素材优先级固定为：
   已归档论文图（A 级）→ 已归档网页图 → 真实数据图表库 → 生图兜底；
   引用论文图/网页的页面写来源图注，演讲备注给出可照读讲稿。
3. 用户要求"图片太少 / 能换的都换"时，先查对照表里未用的 A 级资产，
   空间不足就新增"证据页"集中放 2-4 张相关论文图。
4. 验收：逐页 lint（或单页例外截图核验）→ 回读页序/页码/图落地核对 →
   改动页截图目检 → `drive +export` 导出 PPTX → present_files 双交付
   （在线链接 + 本地 PPTX）。

## 交付物标准

- 调研报告 / 资料索引：`资料归档\00-资料索引与备注.md`（含全部来源）。
- 论文资产：`论文图片素材\`（PNG/CSV + `_manifest.json` + 提取索引 + 对照表）。
- PPT：在线 Slides + 本地 PPTX，页脚来源可追溯，无编造数据。
