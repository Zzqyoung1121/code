# 本地启动与同步脚本

## 启动 UI
### Linux / macOS
```bash
python3 scripts/serve.py --port 8000 --open
```

### Windows (BAT)
```bat
scripts\serve.bat
```

## 同步 OI-wiki 目录（元数据）
```bash
python3 scripts/sync_oiwiki_catalog.py
```

- 默认端口：8000
- BAT 会自动打开 `ui/index.html`
- BAT 优先使用 `py`，不存在时回退到 `python`
- 同步脚本只抓目录元数据（title/url/oid），不抓文章正文
