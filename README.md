# research-to-ppt

将「主题调研 → 资料搜索与归档 → 论文资产（figures/tables）提取 → 用户选模板 → 尽量复用归档资产生成 PPT」固化为一条可复用的 Agent 工作流 Skill。

## 工作流（四阶段闭环）

```
调研内容 → 搜索资料 → 下载成可论文引用的 source（含 figures）→ 生成 PPT（先选模板，尽量多调用已归档资产）
```

| 阶段 | 做什么 | 产物 |
|---|---|---|
| A 调研 | 拆解主题、定信息需求 | 需求清单 |
| B 归档 | 搜索 + 精读 + 下载成可引用资产 | `资料归档\` + 总索引（含 A/B/C 引用分级） |
| C 提取 | 论文 figures/tables 批量提取 + 分级 + token 映射 | `论文图片素材\` + manifest + 逐页对照表 |
| D PPT | 先让用户选模板 → 资产优先 → 逐页 lint/截图 → 双交付 | 在线 Slides + 本地 PPTX |

## 目录结构

```
research-to-ppt/
├── SKILL.md                        # 主工作流（四阶段总览 + 每阶段要点 + 交付标准）
├── scripts/
│   └── extract_pdf_assets.py       # 批量提取论文图片与表格（PNG/CSV + _manifest.json + 索引）
└── references/
    ├── research-archive.md         # 阶段 A/B 细则：搜索优先级、归档目录、索引格式、A/B/C 分级
    ├── pdf-asset-extraction.md     # 阶段 C 细则：提取命令、目检要求、上传拿 token、对照表
    └── ppt-generation.md           # 阶段 D 细则：模板选择、资产调用优先级、来源纪律、验收清单
```

## 核心规则

1. **先让用户选模板**：做 PPT 前先询问模板偏好（默认学术 / 简洁商务 / 用户自备 / 复刻样例），选定后全程遵守。
2. **资产优先**：素材优先级固定为 已归档论文图（A 级）→ 已归档网页图 → 真实数据图表库 → 生图兜底。
3. **来源可追溯**：每个关键数字记录来源（标题 + URL + 日期），引用论文图的页面写「图：标题（论文名 p页码）」。
4. **可迭代补图**：用户要求"图片太少 / 能换的都换"时，先查对照表中未用的 A 级资产，空间不足就新增"证据页"。

## 快速开始（阶段 C 核心命令）

```bash
python scripts/extract_pdf_assets.py <pdf1> [pdf2 ...] \
  --out "资料归档/论文图片素材" --index [--dedup-close]
```

依赖：PyMuPDF（`pip install PyMuPDF`）。
