# 本地启动脚本

本目录提供可直接运行的本地服务脚本，启动后默认打开 UI 首页（`ui/index.html`）。

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
- BAT 会自动打开 `ui/index.html`
- BAT 优先使用 `py`，不存在时回退到 `python`
