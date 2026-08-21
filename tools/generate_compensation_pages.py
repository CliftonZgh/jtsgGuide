#!/usr/bin/env python3
"""Generate compensation-standard Markdown pages from a CSV file."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = {"year", "province", "city"}
FIELD_LABELS = {
    "medical": "医疗费",
    "hospital_meal": "住院伙食补助费",
    "accommodation": "住宿费",
    "nutrition": "营养费",
    "care": "护理费",
    "lost_work": "误工费",
    "traffic": "交通费",
    "follow_up": "后续治疗费",
    "disability_base": "残疾赔偿金基数",
    "death_base": "死亡赔偿金基数",
    "notes": "备注",
}
DEFAULT_NOTES = {
    "medical": "需要与事故相关的正规医疗票据、费用明细和病历材料。",
    "hospital_meal": "按实际住院天数和适用地区标准核对。",
    "accommodation": "仅记录必要、合理且有凭证的住宿支出。",
    "nutrition": "通常需要医嘱或鉴定意见支持营养期限和必要性。",
    "care": "核对护理期限、护理人数、护理方式和护理证明。",
    "lost_work": "优先按实际收入减少计算，并保存误工和收入证明。",
    "traffic": "仅记录就医、复诊、鉴定等必要且合理的交通支出。",
    "follow_up": "根据医嘱、鉴定意见或实际发生的后续治疗费用核对。",
    "disability_base": "需要结合伤残等级、年龄、适用地区和赔偿年限核算。",
    "death_base": "需要结合死亡人员年龄、适用地区和赔偿年限核算。",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate compensation-standard pages and a yearly index from CSV."
    )
    parser.add_argument("--csv", required=True,
                        type=Path, help="Input CSV path")
    parser.add_argument("--year", type=int, help="Only generate this year")
    parser.add_argument(
        "--docs-dir", type=Path, default=Path("docs"), help="MkDocs docs directory"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing generated pages"
    )
    return parser.parse_args()


def clean(value: str | None) -> str:
    return (value or "").strip()


def safe_name(value: str) -> str:
    return value.replace("/", "／").replace("\\", "＼").strip()


def read_rows(csv_path: Path, selected_year: int | None) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"CSV 缺少必需列: {names}")

        rows = []
        for line_number, raw_row in enumerate(reader, start=2):
            row = {key: clean(value) for key, value in raw_row.items()}
            if not row["year"] or not row["province"]:
                raise ValueError(f"CSV 第 {line_number} 行缺少 year 或 province")
            try:
                year = int(row["year"])
            except ValueError as error:
                raise ValueError(
                    f"CSV 第 {line_number} 行的 year 不是整数") from error
            if selected_year is not None and year != selected_year:
                continue
            row["year"] = str(year)
            rows.append(row)

    if not rows:
        target = selected_year if selected_year is not None else "CSV 中的年度"
        raise ValueError(f"没有找到 {target} 的数据")
    return rows


def page_path(root: Path, row: dict[str, str]) -> Path:
    year_dir = root / "赔偿标准" / row["year"] / safe_name(row["province"])
    filename = f"{safe_name(row['city'])}.md" if row["city"] else "省级标准.md"
    return year_dir / filename


def page_title(row: dict[str, str]) -> str:
    location = row["province"] if not row["city"] else f"{row['province']}{row['city']}"
    return f"{row['year']} 年{location}交通事故赔偿标准"


def standard_rows(row: dict[str, str]) -> str:
    lines = [
        "| 序号 | 项目 | 赔偿标准 | 来源 / 备注 |",
        "| ---: | --- | --- | --- |",
    ]
    items = [
        ("medical", "按票据据实计算"),
        ("hospital_meal", "待补录：按住院天数计算"),
        ("accommodation", "待补录：按实际合理支出"),
        ("nutrition", "待补录：按营养期限计算"),
        ("care", "待补录：按护理期限、人数和标准计算"),
        ("lost_work", "按实际减少收入或适用口径核算"),
        ("traffic", "按就医、复诊、鉴定等必要支出计算"),
        ("follow_up", "待补录：按医嘱、鉴定意见或实际支出计算"),
        ("disability_base", "待补录：填写适用赔偿基数"),
        ("death_base", "待补录：填写适用赔偿基数"),
    ]
    for number, (field, default) in enumerate(items, start=1):
        value = row.get(field) or default
        note = row.get(f"{field}_note") or DEFAULT_NOTES[field]
        source = row.get("source") or "待补录来源"
        lines.append(
            f"| {number} | {FIELD_LABELS[field]} | {value} | {source}；{note} |")
    return "\n".join(lines)


def render_page(row: dict[str, str]) -> str:
    location = row["province"] if not row["city"] else f"{row['province']}{row['city']}"
    notes = row.get("notes") or "待补充适用条件、文件编号和核验日期"
    source = row.get("source") or "待补录官方来源"
    return f"""# {page_title(row)}

> 速查页：{location}，{row['year']} 年度

本页由 CSV 模板生成。金额、适用条件和计算口径应以事故发生地在 {row['year']} 年适用的权威文件、保险合同和办案机关要求为准。

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 适用年度 | {row['year']} 年 |
| 适用地区 | {location} |
| 来源 | {source} |
| 备注 | {notes} |

## 赔偿项目清单

{standard_rows(row)}

## 伤残等级清单

| 伤残等级 | 赔偿指数 | {row['year']} 年金额 | 备注 |
| --- | ---: | --- | --- |
| 一级 | 100% | 待补录 | 以适用基数和赔偿年限核算 |
| 二级 | 90% | 待补录 | 以适用基数和赔偿年限核算 |
| 三级 | 80% | 待补录 | 以适用基数和赔偿年限核算 |
| 四级 | 70% | 待补录 | 以适用基数和赔偿年限核算 |
| 五级 | 60% | 待补录 | 以适用基数和赔偿年限核算 |
| 六级 | 50% | 待补录 | 以适用基数和赔偿年限核算 |
| 七级 | 40% | 待补录 | 以适用基数和赔偿年限核算 |
| 八级 | 30% | 待补录 | 以适用基数和赔偿年限核算 |
| 九级 | 20% | 待补录 | 以适用基数和赔偿年限核算 |
| 十级 | 10% | 待补录 | 以适用基数和赔偿年限核算 |

!!! warning "使用边界"
    本页不是官方标准，也不构成法律、医疗或保险意见。伤残等级应以具有资质的鉴定机构意见为准，具体赔偿应结合责任、证据和保险范围核算。
"""


def render_index(year: str, rows: list[dict[str, str]]) -> str:
    lines = [
        f"# {year} 年交通事故赔偿标准",
        "",
        f"> 年度地区索引：{year} 年",
        "",
        "本页由 CSV 模板生成。省级行链接到省级标准页，填写城市的行链接到该城市独立页面。",
        "",
        "| 序号 | 省、市、自治区 | 页面 | 状态 |",
        "| ---: | --- | --- | --- |",
    ]
    for number, row in enumerate(rows, start=1):
        province = row["province"]
        city = row["city"]
        label = province if not city else f"{province}{city}"
        relative = f"{safe_name(province)}/{safe_name(city) if city else '省级标准'}.md"
        status = row.get("status") or (
            "待补录" if not row.get("source") else "已录入来源")
        lines.append(
            f"| {number} | {label} | [{label}]({relative}) | {status} |")
    return "\n".join(lines) + "\n"


def write_text(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def generate(rows: list[dict[str, str]], docs_dir: Path, force: bool) -> tuple[int, int]:
    written = 0
    skipped = 0
    by_year: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_year.setdefault(row["year"], []).append(row)
        path = page_path(docs_dir, row)
        if write_text(path, render_page(row), force):
            written += 1
        else:
            skipped += 1

    for year, year_rows in by_year.items():
        index_path = docs_dir / "赔偿标准" / year / "城市索引.md"
        if write_text(index_path, render_index(year, year_rows), force):
            written += 1
        else:
            skipped += 1
    return written, skipped


def main() -> int:
    args = parse_args()
    try:
        rows = read_rows(args.csv, args.year)
        written, skipped = generate(rows, args.docs_dir, args.force)
    except (OSError, ValueError) as error:
        print(f"错误: {error}")
        return 1
    print(f"已生成或更新 {written} 个文件，跳过 {skipped} 个已存在文件。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
