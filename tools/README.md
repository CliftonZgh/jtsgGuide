# 赔偿标准批量生成工具

`generate_compensation_pages.py` 使用 CSV 数据生成赔偿标准 Markdown 页面和年度城市索引，不需要第三方 Python 包。

## CSV 模板

模板文件为 `赔偿标准模板.csv`。每一行表示一个省级地区或城市：

- `year`：年度，例如 `2026`
- `province`：省、自治区或直辖市名称
- `city`：城市名称；省级页面留空
- `status`：索引中显示的状态
- `source`：正式文件名称、链接或来源说明
- `medical` 至 `death_base`：各赔偿项目的已核验标准
- `notes`：适用条件、发布日期、核验日期等补充说明

## 生成某一年的页面

在项目根目录执行：

```bash
python3 tools/generate_compensation_pages.py \
  --csv tools/赔偿标准模板.csv \
  --year 2026
```

脚本会生成：

```text
docs/赔偿标准/2026/城市索引.md
docs/赔偿标准/2026/北京市/省级标准.md
docs/赔偿标准/2026/广东省/省级标准.md
docs/赔偿标准/2026/广东省/广州市.md
```

默认不会覆盖已经存在的页面。确认 CSV 内容无误、需要重新生成时，再使用：

```bash
python3 tools/generate_compensation_pages.py \
  --csv tools/赔偿标准模板.csv \
  --year 2026 \
  --force
```

## 生成多个年度

CSV 可以包含多个年度。不传 `--year` 时，脚本会按 CSV 中出现的所有年度分别生成：

```bash
python3 tools/generate_compensation_pages.py \
  --csv tools/赔偿标准模板.csv
```

生成后需要在 `mkdocs.yml` 的 `nav` 中加入新页面。脚本不会自动修改导航，避免批量生成时覆盖人工调整过的导航层级。

## 建议流程

1. 复制模板或在模板中追加完整的省市行。
2. 只填入已核验的官方标准，未知值留空。
3. 先不使用 `--force` 试运行，确认跳过和生成数量。
4. 检查生成页面和年度索引。
5. 更新 `mkdocs.yml` 导航。
6. 执行 `mkdocs build --strict`。

脚本生成的是信息整理页面，不会判断责任比例、伤残等级或最终应赔金额。
