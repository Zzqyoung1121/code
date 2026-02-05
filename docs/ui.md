# 本地与云端 UI 规划（OI-wiki 风格）

本地与云端 UI 保持一致：统一使用 `ui/index.html` 作为入口。

## 设计原则
- UI 仿照 OI-wiki 的“条目 + 评论区”感受。
- 每个算法条目只保留评论区域。
- 评论内容即用户发布的模板（板子），等价于“博客/专栏帖子”。

## 数据结构
- `ui/catalog.json`：OI-wiki 目录链接元数据（标题 + URL + oid）
- `ui/user_templates.json`：用户模板评论数据（按 oid 映射）

## 云端发布（像博客/专栏）
- 用户直接在云端修改 `ui/user_templates.json`（例如 GitHub 网页编辑）并提交。
- 合并后，UI 自动显示新模板评论。

## OI-wiki 目录同步
- 运行 `python3 scripts/sync_oiwiki_catalog.py` 同步目录到 `ui/catalog.json`。
- 脚本只同步目录元数据，不搬运原文内容。
