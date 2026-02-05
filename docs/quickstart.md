# 快速启动

本项目无需编译；直接启动本地服务即可浏览 UI。

## 本地启动
### Linux / macOS
```bash
python3 scripts/serve.py --port 8000 --open
```

### Windows（BAT）
```bat
scripts\serve.bat
```
指定端口：
```bat
scripts\serve.bat 9000
```

## 云端模式（像博客/专栏发布模板）
1) 打开 `ui/user_templates.json`。  
2) 追加你的模板帖子（user/title/link/time）。  
3) 提交后页面自动展示。  

## OI-wiki 目录同步（可选）
```bash
python3 scripts/sync_oiwiki_catalog.py
```
说明：仅同步目录链接与标题，不复制 OI-wiki 原文。
