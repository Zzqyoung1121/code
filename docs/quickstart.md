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
如果双击/执行 BAT 无法打开，请改用 CMD：
```bat
scripts\serve.cmd
```
指定端口：
```bat
scripts\serve.bat 9000
```
指定 host（可选，默认 0.0.0.0）：
```bat
scripts\serve.bat 9000 0.0.0.0
```

## 其他电脑访问（同一局域网）
- 使用 BAT 输出的 `LAN URL`，不要用 `localhost`。
- 若脚本提示未管理员运行，请用“管理员 CMD”重启 BAT（用于自动加防火墙规则）。
- 确保两台设备在同一网段（如都在 `192.168.1.*`）。
- 路由器/热点若开启 AP Isolation（客户端隔离），请关闭。

## OI-Wiki 全量分类
- UI 已支持加载完整分类树（不再截断条目数量）。
- 运行 `python3 scripts/sync_oiwiki_catalog.py` 可同步 OI-Wiki 元数据到 `ui/catalog.json`。
- 若网络受限导致同步失败，请在可联网环境执行后将 `ui/catalog.json` 拷贝回来。

## 批量删除模板
- 在列表中勾选条目（或使用“全选/反选”）。
- 点击“批量删除”一次删除多条。


## Windows 报错“此时不应有 .”
- 已修复 `scripts\serve.bat` 的解析兼容问题。
- 请拉取最新代码后重新执行：`scripts\serve.bat 8000`。
