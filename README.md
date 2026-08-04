# 交通事故处理指南（MkDocs）

本项目使用 MkDocs 构建静态网站，内容聚焦于交通事故发生后的规范处理流程。

## 1. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 本地启动

```bash
mkdocs serve
```

浏览器访问：

- <http://127.0.0.1:8000>

## 3. 构建静态站点

```bash
mkdocs build
```

构建产物位于 `site/` 目录。
