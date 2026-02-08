# 本地与云端 UI 规划（完全 OI-Wiki 风格）

当前 UI 采用 OI-Wiki 风格布局：
- 顶部深色导航栏
- 左侧分类导航树（完整加载 catalog 中的分类/条目）
- 中间主内容（板子列表、详情、编辑）
- 右侧说明栏

## 三个关键能力
1. **局域网访问**：服务默认监听 `0.0.0.0`，可从其他电脑访问。  
2. **完整分类树**：`ui/catalog.json` 可承载 OI-Wiki 全量目录，UI 不截断显示。  
3. **批量删除**：列表勾选 + 全选/反选 + 批量删除。

## 数据模型
- 分类目录：`ui/catalog.json`（section / items / oid）
- 用户模板：浏览器本地 `localStorage.snippetsDB`（包含 category + oid + markdown）

## 目录同步
```bash
python3 scripts/sync_oiwiki_catalog.py
```
说明：仅同步目录元数据，不复制 OI-Wiki 正文。
