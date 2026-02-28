import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import base64
import io
import json

try:
    from PIL import Image, ImageGrab, ImageTk
except ImportError:  # pragma: no cover - optional dependency
    Image = None
    ImageGrab = None
    ImageTk = None


class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated Paint")
        self.root.attributes("-topmost", True)

        self.scale_factor = 1.0
        self.min_scale = 0.2
        self.max_scale = 4.0
        self.current_item = None
        self.draw_color = "#000000"
        self.tool = tk.StringVar(value="pencil")
        self.selected_item = None
        self.item_widths = {}
        self.objects = {}
        self.object_order = []
        self.object_names = {}
        self.image_refs = {}
        self.image_sources = {}
        self.text_sizes = {}
        self.undo_stack = []
        self.redo_stack = []
        self.is_restoring = False

        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.toolbar = ttk.Frame(main_frame, padding=8)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(self.toolbar, text="工具").pack(side=tk.LEFT, padx=(0, 6))
        for name, label in [("pencil", "铅笔"), ("eraser", "橡皮擦")]:
            ttk.Radiobutton(
                self.toolbar,
                text=label,
                value=name,
                variable=self.tool,
                command=self.on_tool_change,
            ).pack(side=tk.LEFT, padx=4)

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=6
        )
        ttk.Label(self.toolbar, text="颜色").pack(side=tk.LEFT, padx=(0, 6))
        self.color_choice = ttk.Combobox(
            self.toolbar,
            values=["黑色", "红色", "蓝色", "绿色", "紫色"],
            state="readonly",
            width=8,
        )
        self.color_choice.set("黑色")
        self.color_choice.pack(side=tk.LEFT, padx=4)
        self.color_choice.bind("<<ComboboxSelected>>", self.on_color_change)

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=6
        )
        ttk.Button(self.toolbar, text="粘贴文字", command=self.paste_text).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(self.toolbar, text="粘贴图片", command=self.paste_image).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(self.toolbar, text="打开", command=self.open_file).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(self.toolbar, text="保存", command=self.save_file).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(self.toolbar, text="置顶", command=self.bring_to_front).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(self.toolbar, text="删除选中", command=self.delete_selected).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(self.toolbar, text="清空", command=self.clear_canvas).pack(
            side=tk.LEFT, padx=4
        )

        self.canvas = tk.Canvas(main_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.status = ttk.Label(
            self.root,
            text="工具: 铅笔 | 中键拖动平移 | 滚轮缩放",
        )
        self.status.pack(fill=tk.X)

        self._reset_scrollregion()

    def _bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<ButtonPress-3>", self.on_right_click)
        self.canvas.bind("<ButtonPress-2>", self.on_middle_down)
        self.canvas.bind("<B2-Motion>", self.on_middle_drag)
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.root.bind("<Delete>", self.on_delete_key)
        self.root.bind("<Control-z>", self.on_undo)
        self.root.bind("<Control-y>", self.on_redo)
        self.root.bind("<Control-s>", self.save_file)
        self.root.bind("<Control-o>", self.open_file)

    def _reset_scrollregion(self):
        size = 5000
        self.canvas.config(scrollregion=(-size, -size, size, size))

    def on_tool_change(self):
        self.clear_selection()
        self.status.config(text=f"工具: {self.tool.get()}")

    def on_color_change(self, event):
        mapping = {
            "黑色": "#000000",
            "红色": "#d32f2f",
            "蓝色": "#1976d2",
            "绿色": "#2e7d32",
            "紫色": "#6a1b9a",
        }
        self.draw_color = mapping.get(self.color_choice.get(), "#000000")

    def on_middle_down(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def on_middle_drag(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_mouse_wheel(self, event):
        direction = 1 if event.delta > 0 else -1
        factor = 1.1 if direction > 0 else 0.9
        new_scale = max(self.min_scale, min(self.max_scale, self.scale_factor * factor))
        factor = new_scale / self.scale_factor
        self.scale_factor = new_scale

        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        self.canvas.scale("all", canvas_x, canvas_y, factor, factor)
        self._rescale_special_items()
        self._expand_scrollregion(canvas_x, canvas_y)

    def _expand_scrollregion(self, x, y):
        left, top, right, bottom = self.canvas.bbox("all") or (-100, -100, 100, 100)
        padding = 1000
        self.canvas.config(
            scrollregion=(
                min(left, x - padding),
                min(top, y - padding),
                max(right, x + padding),
                max(bottom, y + padding),
            )
        )

    def on_mouse_down(self, event):
        tool = self.tool.get()
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        if tool == "eraser":
            self.erase_at(canvas_x, canvas_y)
            return

        if tool == "pencil":
            self.current_item = self.canvas.create_line(
                canvas_x,
                canvas_y,
                canvas_x,
                canvas_y,
                fill=self.draw_color,
                width=2,
                capstyle=tk.ROUND,
                smooth=True,
            )

    def on_mouse_move(self, event):
        tool = self.tool.get()
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        if tool == "eraser":
            self.erase_at(canvas_x, canvas_y)
            return

        if tool == "pencil" and self.current_item:
            coords = self.canvas.coords(self.current_item)
            coords.extend([canvas_x, canvas_y])
            self.canvas.coords(self.current_item, *coords)
            self._expand_scrollregion(canvas_x, canvas_y)

    def on_mouse_up(self, event):
        tool = self.tool.get()
        if tool == "pencil" and self.current_item:
            item_id = self.current_item
            name = f"stroke-{len(self.object_order) + 1}"
            self.objects[item_id] = "stroke"
            self.object_order.append(item_id)
            self.object_names[item_id] = name
            self.item_widths[item_id] = 2
            self._record_action(
                {
                    "type": "create",
                    "item_id": item_id,
                    "snapshot": self._snapshot_item(item_id),
                }
            )
            self.current_item = None

    def erase_at(self, x, y):
        hits = self.canvas.find_overlapping(x - 2, y - 2, x + 2, y + 2)
        for item_id in hits:
            if item_id in self.objects:
                self.remove_item(item_id)

    def clear_selection(self):
        if self.selected_item:
            original = self.item_widths.get(self.selected_item)
            if original:
                self.canvas.itemconfigure(self.selected_item, width=original)
        self.selected_item = None

    def delete_selected(self):
        if self.selected_item:
            self.remove_item(self.selected_item)
        self.clear_selection()

    def remove_item(self, item_id, record=True):
        if record:
            snapshot = self._snapshot_item(item_id)
            if snapshot:
                self._record_action(
                    {"type": "delete", "snapshot": snapshot, "item_id": item_id}
                )
        self.canvas.delete(item_id)
        if item_id in self.objects:
            del self.objects[item_id]
        if item_id in self.object_names:
            del self.object_names[item_id]
        if item_id in self.object_order:
            self.object_order.remove(item_id)
        if item_id in self.item_widths:
            del self.item_widths[item_id]
        if item_id in self.image_refs:
            del self.image_refs[item_id]
        if item_id in self.image_sources:
            del self.image_sources[item_id]
        if item_id in self.text_sizes:
            del self.text_sizes[item_id]

    def clear_canvas(self):
        if not self.is_restoring:
            snapshots = [self._snapshot_item(item_id) for item_id in list(self.objects)]
            snapshots = [snap for snap in snapshots if snap]
            if snapshots:
                self._record_action({"type": "clear", "snapshots": snapshots})
        self.canvas.delete("all")
        self.objects.clear()
        self.object_order.clear()
        self.object_names.clear()
        self.item_widths.clear()
        self.selected_item = None
        self.image_refs.clear()
        self.image_sources.clear()
        self.text_sizes.clear()
        self._reset_scrollregion()

    def on_delete_key(self, event):
        self.delete_selected()

    def on_right_click(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        hits = self.canvas.find_overlapping(
            canvas_x - 2, canvas_y - 2, canvas_x + 2, canvas_y + 2
        )
        if not hits:
            self.clear_selection()
            return
        item_id = hits[-1]
        if item_id not in self.objects:
            self.clear_selection()
            return
        self.clear_selection()
        self.selected_item = item_id
        try:
            current_width = int(self.canvas.itemcget(item_id, "width") or 1)
        except tk.TclError:
            current_width = None
        if current_width:
            self.item_widths[item_id] = current_width
            self.canvas.itemconfigure(item_id, width=current_width + 1)

    def bring_to_front(self):
        if self.selected_item:
            self.canvas.tag_raise(self.selected_item)

    def _rescale_special_items(self):
        for item_id, item_type in self.objects.items():
            if item_type == "text" and item_id in self.text_sizes:
                base_size = self.text_sizes[item_id]
                new_size = max(1, int(round(base_size * self.scale_factor)))
                font_family = self.canvas.itemcget(item_id, "font").split()[0] or "Arial"
                self.canvas.itemconfigure(item_id, font=(font_family, new_size))
            elif item_type == "image" and item_id in self.image_sources:
                source = self.image_sources[item_id]
                new_width = max(1, int(round(source.width * self.scale_factor)))
                new_height = max(1, int(round(source.height * self.scale_factor)))
                resized = source.resize((new_width, new_height))
                tk_image = ImageTk.PhotoImage(resized)
                self.image_refs[item_id] = tk_image
                self.canvas.itemconfigure(item_id, image=tk_image)

    def paste_text(self):
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            messagebox.showinfo("提示", "剪贴板没有文本内容。")
            return
        if not text.strip():
            messagebox.showinfo("提示", "剪贴板没有文本内容。")
            return

        canvas_x = self.canvas.canvasx(self.canvas.winfo_width() / 2)
        canvas_y = self.canvas.canvasy(self.canvas.winfo_height() / 2)
        item_id = self.canvas.create_text(
            canvas_x,
            canvas_y,
            text=text,
            fill=self.draw_color,
            anchor=tk.CENTER,
            font=("Arial", 14),
        )
        name = f"text-{len(self.object_order) + 1}"
        self.objects[item_id] = "text"
        self.text_sizes[item_id] = 14
        self.object_order.append(item_id)
        self.object_names[item_id] = name
        self._record_action(
            {"type": "create", "item_id": item_id, "snapshot": self._snapshot_item(item_id)}
        )
        self._expand_scrollregion(canvas_x, canvas_y)

    def paste_image(self):
        if ImageGrab is None or ImageTk is None:
            messagebox.showwarning(
                "提示", "当前环境未安装 Pillow，无法从剪贴板粘贴图片。"
            )
            return
        image = ImageGrab.grabclipboard()
        if image is None:
            messagebox.showinfo("提示", "剪贴板没有图片内容。")
            return

        tk_image = ImageTk.PhotoImage(image)

        canvas_x = self.canvas.canvasx(self.canvas.winfo_width() / 2)
        canvas_y = self.canvas.canvasy(self.canvas.winfo_height() / 2)
        item_id = self.canvas.create_image(
            canvas_x, canvas_y, image=tk_image, anchor=tk.CENTER
        )
        self.image_refs[item_id] = tk_image
        self.image_sources[item_id] = image
        name = f"image-{len(self.object_order) + 1}"
        self.objects[item_id] = "image"
        self.object_order.append(item_id)
        self.object_names[item_id] = name
        self._record_action(
            {"type": "create", "item_id": item_id, "snapshot": self._snapshot_item(item_id)}
        )
        self._expand_scrollregion(canvas_x, canvas_y)

    def save_file(self, event=None):
        path = filedialog.asksaveasfilename(
            title="保存",
            defaultextension=".zpaint",
            filetypes=[("ZPaint 文件", "*.zpaint")],
        )
        if not path:
            return

        payload = {
            "format": "zpaint-v1",
            "scale_factor": self.scale_factor,
            "items": self._serialize_items(),
        }
        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False)
            self.status.config(text=f"已保存: {path}")
        except OSError as exc:
            messagebox.showerror("保存失败", f"无法保存文件:\n{exc}")

    def open_file(self, event=None):
        path = filedialog.askopenfilename(
            title="打开",
            filetypes=[("ZPaint 文件", "*.zpaint")],
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as file:
                payload = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("打开失败", f"无法读取文件:\n{exc}")
            return

        if payload.get("format") != "zpaint-v1":
            messagebox.showerror("打开失败", "文件格式不受支持。")
            return

        self.clear_canvas()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.scale_factor = float(payload.get("scale_factor", 1.0))

        for snapshot in payload.get("items", []):
            self._restore_serialized_snapshot(snapshot)

        self._rescale_special_items()
        self.status.config(text=f"已打开: {path}")

    def _serialize_items(self):
        snapshots = []
        for item_id in self.object_order:
            snapshot = self._snapshot_item(item_id)
            if not snapshot:
                continue
            if snapshot["item_type"] == "image":
                source = snapshot.get("image")
                if source is None or Image is None:
                    continue
                buffer = io.BytesIO()
                source.save(buffer, format="PNG")
                snapshot["image"] = base64.b64encode(buffer.getvalue()).decode("ascii")
            snapshots.append(snapshot)
        return snapshots

    def _restore_serialized_snapshot(self, snapshot):
        if snapshot.get("item_type") == "image":
            encoded = snapshot.get("image")
            if not encoded:
                return None
            if Image is None or ImageTk is None:
                return None
            image_bytes = base64.b64decode(encoded.encode("ascii"))
            source = Image.open(io.BytesIO(image_bytes)).copy()
            snapshot = dict(snapshot)
            snapshot["image"] = source
        return self._restore_snapshot(snapshot)

    def _snapshot_item(self, item_id):
        item_type = self.objects.get(item_id)
        if not item_type:
            return None
        snapshot = {
            "item_type": item_type,
            "coords": self.canvas.coords(item_id),
            "options": {
                "fill": self.canvas.itemcget(item_id, "fill"),
                "width": self.canvas.itemcget(item_id, "width"),
            },
        }
        if item_type == "stroke":
            snapshot["options"]["capstyle"] = self.canvas.itemcget(item_id, "capstyle")
            snapshot["options"]["smooth"] = self.canvas.itemcget(item_id, "smooth")
        elif item_type == "text":
            snapshot["text"] = self.canvas.itemcget(item_id, "text")
            snapshot["font"] = self.canvas.itemcget(item_id, "font")
            snapshot["size"] = self.text_sizes.get(item_id, 14)
        elif item_type == "image":
            snapshot["image"] = self.image_sources.get(item_id)
        return snapshot

    def _restore_snapshot(self, snapshot):
        item_type = snapshot["item_type"]
        coords = snapshot["coords"]
        if item_type == "stroke":
            item_id = self.canvas.create_line(
                *coords,
                fill=snapshot["options"]["fill"],
                width=float(snapshot["options"]["width"] or 2),
                capstyle=snapshot["options"].get("capstyle", tk.ROUND),
                smooth=bool(snapshot["options"].get("smooth", True)),
            )
            self.item_widths[item_id] = 2
        elif item_type == "text":
            item_id = self.canvas.create_text(
                coords[0],
                coords[1],
                text=snapshot["text"],
                fill=snapshot["options"]["fill"],
                anchor=tk.CENTER,
                font=snapshot["font"],
            )
            self.text_sizes[item_id] = snapshot.get("size", 14)
        elif item_type == "image":
            source = snapshot.get("image")
            if source is None:
                return None
            tk_image = ImageTk.PhotoImage(source)
            item_id = self.canvas.create_image(
                coords[0], coords[1], image=tk_image, anchor=tk.CENTER
            )
            self.image_refs[item_id] = tk_image
            self.image_sources[item_id] = source
        else:
            return None
        name = f"{item_type}-{len(self.object_order) + 1}"
        self.objects[item_id] = item_type
        self.object_order.append(item_id)
        self.object_names[item_id] = name
        return item_id

    def _record_action(self, action):
        if self.is_restoring:
            return
        self.undo_stack.append(action)
        self.redo_stack.clear()

    def on_undo(self, event=None):
        if not self.undo_stack:
            return
        action = self.undo_stack.pop()
        self.is_restoring = True
        try:
            if action["type"] == "create":
                item_id = action["item_id"]
                if item_id in self.objects:
                    self.remove_item(item_id, record=False)
                self.redo_stack.append(action)
            elif action["type"] == "delete":
                snapshot = action["snapshot"]
                item_id = self._restore_snapshot(snapshot)
                if item_id:
                    action["item_id"] = item_id
                    self.redo_stack.append(action)
            elif action["type"] == "clear":
                restored = []
                for snapshot in action["snapshots"]:
                    item_id = self._restore_snapshot(snapshot)
                    if item_id:
                        restored.append(item_id)
                if restored:
                    self.redo_stack.append({"type": "clear", "snapshots": action["snapshots"]})
        finally:
            self.is_restoring = False

    def on_redo(self, event=None):
        if not self.redo_stack:
            return
        action = self.redo_stack.pop()
        self.is_restoring = True
        try:
            if action["type"] == "create":
                item_id = self._restore_snapshot(action["snapshot"])
                if item_id:
                    action["item_id"] = item_id
                    self.undo_stack.append(action)
            elif action["type"] == "delete":
                item_id = action.get("item_id")
                if item_id and item_id in self.objects:
                    self.remove_item(item_id, record=False)
                    self.undo_stack.append(action)
            elif action["type"] == "clear":
                self.clear_canvas()
                self.undo_stack.append(action)
        finally:
            self.is_restoring = False


if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()
