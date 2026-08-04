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

## 4. 发布到 GitHub Pages（自动）

项目已内置 GitHub Actions 工作流：`.github/workflows/deploy-pages.yml`。

首次启用需要在 GitHub 仓库中设置：

1. 进入仓库 `Settings` -> `Pages`
2. 在 `Build and deployment` 中将 `Source` 设为 `GitHub Actions`
3. 推送到 `main` 分支后会自动触发部署

部署完成后访问：

- <https://cliftonzgh.github.io/jtsgGuide/>
