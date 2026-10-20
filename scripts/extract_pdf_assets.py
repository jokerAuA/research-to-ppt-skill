#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 PDF 论文中提取可引用资产（图片 + 表格）并生成 manifest 清单。

用法:
    python extract_pdf_assets.py <pdf1> [pdf2 ...] --out <输出目录>
                       [--min-area 15000] [--zoom 2.5] [--thumb 240]
                       [--index] [--dedup-close]

行为:
    1. 逐页枚举嵌入图 (page.get_images + image bbox) 与表格 (page.find_tables)
    2. 图片按 bbox 面积阈值筛选; 表格全部提取 (CSV + PNG)
    3. 渲染 PNG (默认 2.5x), 表格 PNG 单独渲染
    4. 写 _manifest.json: 文件名/来源页/xref/bbox/像素/文件大小/判定
    5. --index 时额外生成《00-资产提取索引.md》(按页列出全部资产)

依赖: PyMuPDF (pip install PyMuPDF)
"""
import argparse
import json
import os
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("需要 PyMuPDF: pip install PyMuPDF")

TBL_PAD = 6  # 表格 bbox 外扩像素(pt), 避免裁掉表框


def slugify(pdf_path: Path) -> str:
    return pdf_path.stem.replace(" ", "_").replace("（", "_").replace("）", "_")


def extract_pdf(pdf_path: Path, out_dir: Path, min_area: float, zoom: float,
                thumb: int, index_md: bool, dedup_close: bool) -> dict:
    doc = fitz.open(pdf_path)
    stem = slugify(pdf_path)
    assets = []
    seen_hashes = {}  # dedup: md5 -> (name, bbox)

    for pno in range(doc.page_count):
        page = doc[pno]
        page_assets = []

        # ---------- 图片 ----------
        img_infos = page.get_images(full=True)
        used_rects = []
        for xref, *_ in img_infos:
            try:
                rects = page.get_image_rects(xref)
            except Exception:
                continue
            for r in rects:
                area = abs(r.width * r.height)
                if area < min_area:
                    continue
                if dedup_close:
                    key = hash((round(r.x0, 0), round(r.y0, 0)))
                    if key in seen_hashes:
                        continue
                    seen_hashes[key] = True
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, clip=r)
                name = f"{stem}_p{pno + 1:02d}_fig{len(used_rects) + 1:02d}.png"
                fpath = out_dir / name
                pix.save(fpath)
                used_rects.append(r)
                page_assets.append({
                    "file": name, "kind": "figure", "page": pno + 1,
                    "xref": xref,
                    "bbox_pt": [round(r.x0, 1), round(r.y0, 1),
                                round(r.x1, 1), round(r.y1, 1)],
                    "pixels": [pix.width, pix.height],
                    "size_bytes": fpath.stat().st_size,
                })

        # ---------- 表格 ----------
        try:
            tables = page.find_tables()
        except Exception:
            tables = []
        for ti, tbl in enumerate(tables or []):
            try:
                df = tbl.extract()
                bbox = tbl.bbox
                x0, y0, x1, y1 = bbox
                x0 = max(0, x0 - TBL_PAD); y0 = max(0, y0 - TBL_PAD)
                x1 = min(page.rect.width, x1 + TBL_PAD)
                y1 = min(page.rect.height, y1 + TBL_PAD)
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat,
                                      clip=fitz.Rect(x0, y0, x1, y1))
                base = f"{stem}_p{pno + 1:02d}_table{ti + 1}"
                img_name = base + ".png"
                csv_name = base + ".csv"
                pix.save(out_dir / img_name)
                with open(out_dir / csv_name, "w", encoding="utf-8",
                          newline="") as f:
                    import csv
                    w = csv.writer(f)
                    for row in df:
                        w.writerow([("" if c is None else str(c)) for c in row])
                page_assets.append({
                    "file": img_name, "kind": "table", "page": pno + 1,
                    "csv": csv_name,
                    "rows": len(df), "cols": max((len(r) for r in df), default=0),
                    "bbox_pt": [round(x0, 1), round(y0, 1),
                                round(x1, 1), round(y1, 1)],
                    "pixels": [pix.width, pix.height],
                    "size_bytes": (out_dir / img_name).stat().st_size,
                })
            except Exception as e:
                print(f"[warn] 表格提取失败 {pdf_path.name} p{pno + 1}: {e}")

        assets.extend(page_assets)

    # ---------- manifest ----------
    manifest = {
        "source_pdf": str(pdf_path),
        "title": doc.metadata.get("title", ""),
        "pages": doc.page_count,
        "extracted_at": __import__("datetime").date.today().isoformat(),
        "params": {"min_area_pt2": min_area, "zoom": zoom},
        "assets": assets,
    }
    with open(out_dir / "_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # ---------- 索引 md ----------
    if index_md:
        by_page = {}
        for a in assets:
            by_page.setdefault(a["page"], []).append(a)
        lines = [
            f"# {pdf_path.stem} 资产提取索引",
            "",
            f"- 源文件: `{pdf_path.name}`（{doc.page_count} 页）",
            f"- 提取阈值: 面积 ≥ {min_area} pt²，渲染倍率 {zoom}x",
            f"- 共 {len(assets)} 项资产（图 {sum(1 for a in assets if a['kind']=='figure')} / 表 {sum(1 for a in assets if a['kind']=='table')}）",
            "",
        ]
        for pno in sorted(by_page):
            lines.append(f"## 第 {pno} 页")
            for a in by_page[pno]:
                kind = "图" if a["kind"] == "figure" else "表"
                lines.append(
                    f"- {kind} `{a['file']}` "
                    f"({a['pixels'][0]}×{a['pixels'][1]}px, "
                    f"{a['size_bytes']}B) 页面 bbox={a['bbox_pt']}")
            lines.append("")
        (out_dir / f"00-资产提取索引.md").write_text(
            "\n".join(lines), encoding="utf-8")

    doc.close()
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdfs", nargs="+", help="PDF 论文路径")
    ap.add_argument("--out", required=True, help="输出目录")
    ap.add_argument("--min-area", type=float, default=15000.0,
                    help="图片面积阈值(pt²), 默认 15000")
    ap.add_argument("--zoom", type=float, default=2.5,
                    help="渲染倍率, 默认 2.5")
    ap.add_argument("--index", action="store_true",
                    help="额外生成《00-资产提取索引.md》")
    ap.add_argument("--dedup-close", action="store_true",
                    help="跳过坐标完全相同的重复图(同一图多页复用)")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    all_manifests = []
    for p in args.pdfs:
        pdf = Path(p)
        if not pdf.exists():
            print(f"[skip] 不存在: {pdf}")
            continue
        print(f"[extract] {pdf.name}")
        m = extract_pdf(pdf, out_dir, args.min_area, args.zoom, 240,
                        args.index, args.dedup_close)
        all_manifests.append(m)
        figs = sum(1 for a in m["assets"] if a["kind"] == "figure")
        tbs = sum(1 for a in m["assets"] if a["kind"] == "table")
        print(f"  -> {figs} 图, {tbs} 表, manifest 已写")
    print("完成。输出目录:", out_dir)


if __name__ == "__main__":
    main()
