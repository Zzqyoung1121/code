# 每日金价银价桌面程序

这是一个使用 Python `tkinter` 编写的桌面看板，支持：

- 显示黄金、白银实时价格（美元 `USD/oz` + 人民币 `CNY/oz`）
- 显示美元兑人民币汇率（`USD/CNY`）
- 手动刷新 + 自动刷新（默认每 10 分钟）
- 内置价格走势图（最近 30 个采样点，按人民币计价）
- 网络失败时自动读取本地缓存

## 运行环境

- Python 3.10+
- Tk 图形库（大多数 Python 发行版默认包含）

## 启动方式

```bash
python3 app.py
```

## 数据来源

- 黄金/白银：聚金号公开行情接口（`JO_71` 黄金、`JO_72` 白银）
- 汇率：`open.er-api.com` 的 USD 基准汇率接口

> 若网络不可达，会回退到缓存（或默认汇率）并在界面状态栏提示。

## 本地文件

- `quotes_cache.json`：缓存最新行情 + 汇率 + 历史数据
- `quotes_history.json`：走势图历史记录

## 可自定义项

可在 `app.py` 顶部修改：

- `REFRESH_SECONDS`：自动刷新间隔
- `DEFAULT_USDCNY`：汇率接口失败时的默认汇率
- `MAX_HISTORY_POINTS`：走势图历史点数量
- `CACHE_FILE` / `HISTORY_FILE`：本地缓存文件路径
