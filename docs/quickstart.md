# 快速启动

本项目无需编译；直接启动本地服务即可浏览 UI。

## 本地启动
### Linux / macOS
```bash
python3 scripts/serve.py --host 0.0.0.0 --port 8000 --open
```

### Windows（BAT）
```bat
scripts\serve.bat
```
指定端口：
```bat
scripts\serve.bat 9000
```

## 其他电脑访问（同一局域网）
- 启动后终端会显示：`LAN: http://<你的局域网IP>:8000/ui/index.html`
- 其他电脑请使用这个 LAN 地址访问，而不是 `localhost`。

## OI-Wiki 全量分类
- UI 已支持加载完整分类树（不再截断条目数量）。
- 运行 `python3 scripts/sync_oiwiki_catalog.py` 可同步 OI-Wiki 元数据到 `ui/catalog.json`。
- 若网络受限导致同步失败，请在可联网环境执行后将 `ui/catalog.json` 拷贝回来。

## 批量删除模板
- 在列表中勾选条目（或使用“全选/反选”）。
- 点击“批量删除”一次删除多条。
