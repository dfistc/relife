# ThermoGene Literature Watch

静态文献追踪网站，关注 BMP8B / LONP1 / HMGCS2 在脂肪产热和 PCOS 领域的研究。

## 本地预览

你提供的 Python 路径是开始菜单快捷方式目录。打开其中的
`Python 3.14.lnk`，在 Python 交互窗口中运行：

```python
import http.server, socketserver
socketserver.TCPServer(("", 8000), http.server.SimpleHTTPRequestHandler).serve_forever()
```

然后访问 `http://localhost:8000`。

## 更新流程

`scripts/update_literature.py` 从 Europe PMC 检索 2018 年以来的新候选文献。脚本不会猜测影响因子，也不会自动发布未审阅内容；新候选进入 `data/review_queue.json`，审核主题相关性、期刊指标并生成中英文摘要性概述后，再合并进 `data/papers.json`。

## 公网部署

运行 `scripts/build_public.ps1` 生成仅包含公开网站文件的 `public` 目录。
`.github/workflows/deploy-pages.yml` 会在推送到 GitHub `main` 分支后部署 GitHub Pages。
