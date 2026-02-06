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

- 启动后会输出 Local 与 LAN 地址。
- 其他电脑访问请使用 LAN 地址（不是 localhost）。

## 同步 OI-wiki 目录（元数据）
```bash
python3 scripts/sync_oiwiki_catalog.py
```

- 同步脚本只抓目录元数据（title/url/oid），不抓文章正文
