# 论文资产提取细则（阶段 C）

> 由 SKILL.md 阶段 C 引用。目标：把论文 PDF 里的 figures 与表格批量提取为
> 可直接插入 PPT 的 PNG/CSV 资产，并建立"图 → 论文页 → 用途"映射，让 PPT
> 生成阶段能"尽可能多地调用"真实论文证据。

## 1. 提取命令

```bash
python scripts/extract_pdf_assets.py <pdf1> [pdf2 ...] \
  --out "资料归档/论文图片素材" --index [--dedup-close]
```

- `--min-area 15000`：默认面积阈值（pt²），低于阈值的小图标/水印不提取；
  需要更细的小图可降到 8000。
- `--zoom 2.5`：渲染倍率。横排大图建议 2.5，超宽超扁图（如生成式 AI 条状样本）
  可降到 2.0 防过大；表格建议 3.0（小字表格看不清时重跑 zoom=3）。
- `--index`：自动生成《00-资产提取索引.md》。
- `--dedup-close`：同一图在多页复用（如讲义封面）时只保留首次出现。

产物：每图 `PNG` + 每表 `CSV+PNG` + `_manifest.json`（文件名/来源页/xref/
bbox/像素/大小）+ 索引 md。

## 2. 提取后必做的检查（不能跳过）

1. **逐张目检**：Read 关键图确认内容正确、无乱码/截断；大图按需放大查看。
2. **按 A/B/C 分级**（定义见 research-archive.md §4），在索引 md 中标注。
3. **记录像素与比例**：`_manifest.json` 已含，PPT 写 `<img>` 时按原比例缩放、
   禁止裁剪。
4. 只有内容确认无误的图才能标记"可用"，其余降级或删除。

## 3. 上传与 token 管理（生成 PPT 前）

- 把要用的 A 级图逐个上传到目标幻灯片：
  `lark-cli slides +media-upload --file <图> --presentation <id>`，
  记下各自 `file_token`。
- 保存一张权威映射表（建议 `asset_tokens.json`：图名 → file_token），
  后续每次补图复用，避免重复上传。
- 表格资产若文字过小，优先改为原生 `<table>` 或图表库重建，而非硬插小图。

## 4. 与 PPT 的对应关系

在索引 md 末尾维护"逐页使用建议"小节：

```markdown
## 给 PPT 的使用建议（逐页对照）
- P8 三种公平标准互斥 → usc567_p54_table1（2×2 混淆矩阵）
- P10 COMPAS → cse416_p01_fig01（双人对比评分）、usc567_p43_fig20（评估表单）
- ...
```

PPT 生成阶段直接读这张对照表分配资产；无对照表的页才考虑网页素材/图表库/生图。
