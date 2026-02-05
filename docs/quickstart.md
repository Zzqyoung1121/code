# 快速启动

本项目无需编译；可直接打开 UI 页面，或按需查看 Markdown 文档。

## 本地启动（离线）
### 推荐：启动 UI
```bash
python3 scripts/serve.py --port 8000 --open
```
打开后默认进入：`ui/index.html`

### Windows 一键启动（BAT）
```bat
scripts\serve.bat
```
指定端口：
```bat
scripts\serve.bat 9000
```

## 云端启动（在线）
1) 将仓库推送至 GitHub / GitLab。  
2) 访问 `ui/index.html`。  
3) 按板块查看算法条目下的“用户板子评论”。

## 说明
- 当前 UI 采用“OI-wiki 风格”：每个算法条目下仅保留评论区。
- 评论区中的每条评论就是某个用户发布的板子。
