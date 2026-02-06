# 本地启动与同步脚本

## 启动 UI
### Linux / macOS
```bash
python3 scripts/serve.py --host 0.0.0.0 --port 8000 --open
```

### Windows (BAT)
```bat
scripts\serve.bat
```

指定端口：
```bat
scripts\serve.bat 9000
```

指定端口 + host：
```bat
scripts\serve.bat 9000 0.0.0.0
```

- BAT 会打印 Local URL 和 LAN URL。
- BAT 会尝试自动添加 Windows 防火墙入站规则（管理员模式）。
- 其他电脑访问请使用 LAN URL（不是 localhost）。
- 若仍无法访问：确认同网段，并关闭 AP Isolation。

## 同步 OI-wiki 目录（元数据）
```bash
python3 scripts/sync_oiwiki_catalog.py
```

- 同步脚本只抓目录元数据（title/url/oid），不抓文章正文


## Windows 兼容说明
- 已修复部分 CMD 环境下 `此时不应有 .` 的 bat 解析错误。
- 若你遇到该报错，请更新到最新脚本后重试。
