# 本地启动脚本

本目录提供可直接运行的本地服务脚本，便于浏览 Markdown 索引与模板结构。

## Linux / macOS
```bash
python3 scripts/serve.py --port 8000 --open
```

## Windows (BAT)
```bat
scripts\serve.bat
```

也可以指定端口：
```bat
scripts\serve.bat 9000
```

- 默认端口：8000
- BAT 会自动打开 `docs/index.md`
- BAT 优先使用 `py`，不存在时回退到 `python`
