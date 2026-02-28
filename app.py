#!/usr/bin/env python3
"""桌面贵金属行情看板：显示金/银价格、美元兑人民币汇率和价格走势图。"""

from __future__ import annotations

import json
import re
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from tkinter import BOTH, LEFT, RIGHT, Canvas, StringVar, Tk, ttk
from urllib.request import urlopen

CACHE_FILE = Path("quotes_cache.json")
HISTORY_FILE = Path("quotes_history.json")
REFRESH_SECONDS = 60 * 10
DEFAULT_USDCNY = 7.20
MAX_HISTORY_POINTS = 30


@dataclass
class Quote:
    symbol: str
    name: str
    price_usd: float
    unit: str
    source: str


class JijinhaoProvider:
    """聚金号公开行情接口。"""

    url = "https://api.jijinhao.com/sQuoteCenter/realTime.htm?code=JO_71,JO_72"

    def fetch(self) -> list[Quote]:
        with urlopen(self.url, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")

        mapping = {
            "JO_71": ("黄金", "USD/oz"),
            "JO_72": ("白银", "USD/oz"),
        }
        quotes: list[Quote] = []
        for code, (name, unit) in mapping.items():
            m = re.search(rf'var\s+hq_str_{code}="([^"]+)";', content)
            if not m:
                continue
            fields = m.group(1).split(",")
            if len(fields) < 4:
                continue
            quotes.append(
                Quote(
                    symbol=code,
                    name=name,
                    price_usd=float(fields[3].strip()),
                    unit=unit,
                    source="聚金号",
                )
            )

        if not quotes:
            raise ValueError("未解析到黄金/白银行情")
        return quotes


class FxProvider:
    """获取 USD/CNY 汇率。"""

    url = "https://open.er-api.com/v6/latest/USD"

    def fetch_usdcny(self) -> float:
        with urlopen(self.url, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="ignore"))
        rates = payload.get("rates") or {}
        cny = rates.get("CNY")
        if not cny:
            raise ValueError("汇率接口未返回 CNY")
        return float(cny)


class PreciousMetalsApp:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("每日金价银价桌面看板")
        self.root.geometry("760x540")

        self.status_var = StringVar(value="启动中...")
        self.updated_var = StringVar(value="上次刷新：-")
        self.fx_var = StringVar(value=f"USD/CNY：{DEFAULT_USDCNY:.4f}（默认）")
        self.gold_var = StringVar(value="黄金：--")
        self.silver_var = StringVar(value="白银：--")

        self.provider = JijinhaoProvider()
        self.fx_provider = FxProvider()

        self.canvas = None
        self._build_ui()
        self.refresh_async(initial=True)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill=BOTH, expand=True)

        ttk.Label(frame, text="贵金属行情（美元 + 人民币）", font=("Microsoft YaHei", 20, "bold")).pack(anchor="w")
        ttk.Separator(frame).pack(fill="x", pady=10)

        quote_frame = ttk.Frame(frame)
        quote_frame.pack(fill="x", pady=4)
        ttk.Label(quote_frame, textvariable=self.gold_var, font=("Microsoft YaHei", 12)).pack(anchor="w")
        ttk.Label(quote_frame, textvariable=self.silver_var, font=("Microsoft YaHei", 12)).pack(anchor="w", pady=4)
        ttk.Label(quote_frame, textvariable=self.fx_var, font=("Microsoft YaHei", 11)).pack(anchor="w", pady=4)

        ttk.Label(frame, text="价格走势（最近记录，按人民币计价）", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", pady=(8, 4))
        self.canvas = ttk.LabelFrame(frame, text="走势图", padding=6)
        self.canvas.pack(fill=BOTH, expand=True)
        self.chart = Canvas(self.canvas, bg="#ffffff", height=260, highlightthickness=1, highlightbackground="#cccccc")
        self.chart.pack(fill=BOTH, expand=True)

        info = ttk.Frame(frame)
        info.pack(fill="x", pady=8)
        ttk.Label(info, textvariable=self.updated_var).pack(side=LEFT)
        ttk.Label(info, textvariable=self.status_var, foreground="#336699").pack(side=RIGHT)

        btns = ttk.Frame(frame)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="立即刷新", command=self.refresh_async).pack(side=LEFT)
        ttk.Button(btns, text="退出", command=self.root.destroy).pack(side=RIGHT)

    def refresh_async(self, initial: bool = False) -> None:
        if not initial:
            self.status_var.set("刷新中...")
        threading.Thread(target=self._refresh_worker, daemon=True).start()

    def _refresh_worker(self) -> None:
        err_parts: list[str] = []

        try:
            quotes = self.provider.fetch()
        except Exception as exc:
            quotes, _, _ = self._load_cache()
            err_parts.append(f"行情:{exc}")

        try:
            usdcny = self.fx_provider.fetch_usdcny()
        except Exception as exc:
            _, cached_rate, _ = self._load_cache()
            usdcny = cached_rate or DEFAULT_USDCNY
            err_parts.append(f"汇率:{exc}")

        history = self._load_history()
        now = datetime.now().strftime("%m-%d %H:%M")
        row = {"time": now, "usdcny": usdcny}
        for q in quotes:
            row[q.name] = round(q.price_usd * usdcny, 2)
        if quotes:
            history.append(row)
            history = history[-MAX_HISTORY_POINTS:]
            self._save_history(history)
            self._save_cache(quotes, usdcny, history)

        error = "；".join(err_parts) if err_parts else None
        self.root.after(0, self._update_ui, quotes, usdcny, history, error)
        self.root.after(REFRESH_SECONDS * 1000, self.refresh_async)

    def _update_ui(self, quotes: list[Quote], usdcny: float, history: list[dict], error: str | None) -> None:
        by_name = {q.name: q for q in quotes}
        gold = by_name.get("黄金")
        silver = by_name.get("白银")

        if gold:
            gold_cny = gold.price_usd * usdcny
            self.gold_var.set(
                f"黄金：{gold.price_usd:.2f} USD/oz  |  {gold_cny:.2f} CNY/oz  (来源：{gold.source})"
            )
        if silver:
            silver_cny = silver.price_usd * usdcny
            self.silver_var.set(
                f"白银：{silver.price_usd:.2f} USD/oz  |  {silver_cny:.2f} CNY/oz  (来源：{silver.source})"
            )

        self.fx_var.set(f"USD/CNY：{usdcny:.4f}")
        self.updated_var.set(f"上次刷新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.status_var.set("网络异常，显示缓存" if error and quotes else ("获取失败，请检查网络" if error else "已更新"))
        self._draw_chart(history)

    def _draw_chart(self, history: list[dict]) -> None:
        self.chart.delete("all")
        w = max(self.chart.winfo_width(), 680)
        h = max(self.chart.winfo_height(), 240)
        pad = 30

        if len(history) < 2:
            self.chart.create_text(w / 2, h / 2, text="等待更多数据点以绘制走势图", fill="#666")
            return

        gold_vals = [float(x.get("黄金", 0.0)) for x in history if x.get("黄金")]
        silver_vals = [float(x.get("白银", 0.0)) for x in history if x.get("白银")]
        values = gold_vals + silver_vals
        if not values:
            self.chart.create_text(w / 2, h / 2, text="暂无可用数据", fill="#666")
            return

        vmin, vmax = min(values), max(values)
        if vmin == vmax:
            vmin -= 1.0
            vmax += 1.0

        def xy(i: int, val: float, total: int) -> tuple[float, float]:
            x = pad + (w - 2 * pad) * i / max(total - 1, 1)
            y = h - pad - (h - 2 * pad) * (val - vmin) / (vmax - vmin)
            return x, y

        self.chart.create_rectangle(pad, pad, w - pad, h - pad, outline="#ddd")

        for label, color in (("黄金", "#d4af37"), ("白银", "#8888aa")):
            points = []
            valid = [r for r in history if r.get(label) is not None]
            for i, row in enumerate(valid):
                points.extend(xy(i, float(row[label]), len(valid)))
            if len(points) >= 4:
                self.chart.create_line(*points, fill=color, width=2, smooth=True)
                x_last, y_last = points[-2], points[-1]
                self.chart.create_oval(x_last - 2, y_last - 2, x_last + 2, y_last + 2, fill=color, outline=color)

        self.chart.create_text(pad + 70, pad - 10, text="黄金(CNY/oz)", fill="#a68015")
        self.chart.create_text(pad + 200, pad - 10, text="白银(CNY/oz)", fill="#666699")
        self.chart.create_text(w - pad, h - 10, text=history[-1].get("time", ""), anchor="e", fill="#666")

    def _save_cache(self, quotes: list[Quote], usdcny: float, history: list[dict]) -> None:
        payload = {
            "quotes": [asdict(q) for q in quotes],
            "usdcny": usdcny,
            "history": history,
        }
        CACHE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_cache(self) -> tuple[list[Quote], float, list[dict]]:
        if not CACHE_FILE.exists():
            return [], DEFAULT_USDCNY, []
        try:
            payload = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                # 兼容旧版本缓存结构
                return [Quote(**item) for item in payload], DEFAULT_USDCNY, []
            quotes = [Quote(**item) for item in payload.get("quotes", [])]
            return quotes, float(payload.get("usdcny", DEFAULT_USDCNY)), payload.get("history", [])
        except Exception:
            return [], DEFAULT_USDCNY, []

    def _save_history(self, history: list[dict]) -> None:
        HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_history(self) -> list[dict]:
        if not HISTORY_FILE.exists():
            _, _, hist = self._load_cache()
            return hist or []
        try:
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []


def main() -> None:
    root = Tk()
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    PreciousMetalsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
