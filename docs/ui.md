# 本地与云端 UI 规划（完全 OI-Wiki 风格）

当前 UI 以 OI-Wiki 的交互习惯为目标：
- 顶部深色导航栏
- 左侧分类导航树（按 OI-Wiki 分类/条目）
- 中间文章区（板子列表、详情、编辑）
- 右侧说明/快速入口

## 内容模型
- 分类：来自 `ui/catalog.json`
- 算法条目：每个条目有唯一 `oid`
- 用户模板：本地发布的板子，绑定 `category + oid`

## 发布方式
- 本地发布：在 UI 中“发布板子”直接写 Markdown。
- 云端发布：编辑 `ui/user_templates.json`（可作为云端帖子源），或将导出 JSON 合并到线上仓库。

## 启动
- `python3 scripts/serve.py --open`
- Windows 可用 `scripts\serve.bat`
