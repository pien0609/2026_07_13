"""網站健康檢查工具 — tkinter GUI 入口。"""

import os
import platform
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

try:
    from PIL import Image, ImageTk

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from checker import (
    BROWSERS,
    OUTPUT_DIR,
    check_url,
    clear_history,
    get_history,
    save_check,
    validate_timeout,
    validate_url,
)

# ── 色彩常數 ──────────────────────────────────────────────────
C = {
    "bg": "#0f1923",
    "card": "#172a3a",
    "border": "#1e3a4f",
    "accent": "#00b4d8",
    "accent_lt": "#48cae4",
    "accent_dm": "#0077b6",
    "text": "#e0e6ed",
    "dim": "#7b8794",
    "ok": "#2ecc71",
    "warn": "#f39c12",
    "err": "#e74c3c",
    "btn": "#00b4d8",
    "btn_act": "#48cae4",
    "btn_dis": "#1e3a4f",
    "entry": "#0d1520",
    "log": "#0a1018",
}

FONT = "Microsoft JhengHei"
MONO = "Consolas"


# ── 工具函式 ──────────────────────────────────────────────────


def _open_folder(path: Path) -> None:
    """以系統檔案管理員開啟資料夾。"""
    p = str(path)
    if platform.system() == "Windows":
        os.startfile(p)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", p])
    else:
        subprocess.Popen(["xdg-open", p])


# ══════════════════════════════════════════════════════════════
#  主應用程式
# ══════════════════════════════════════════════════════════════


class HealthCheckApp:
    """網站健康檢查工具主視窗。"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self._checking = False
        self._photo = None  # prevent GC for screenshot preview

        self._setup_window()
        self._setup_style()
        self._create_variables()
        self._build_ui()

    # ── 初始化 ────────────────────────────────────────────────

    def _setup_window(self):
        self.root.title("網站健康檢查工具")
        self.root.geometry("1200x760")
        self.root.minsize(960, 640)
        self.root.configure(bg=C["bg"])
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_style(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure(".", background=C["bg"], foreground=C["text"],
                     font=(FONT, 10))
        s.configure("TFrame", background=C["bg"])
        s.configure("TLabel", background=C["bg"], foreground=C["text"],
                     font=(FONT, 10))
        s.configure("Card.TFrame", background=C["card"])
        s.configure("Card.TLabel", background=C["card"], foreground=C["text"],
                     font=(FONT, 10))
        s.configure("Dim.TLabel", background=C["card"], foreground=C["dim"],
                     font=(FONT, 9))
        s.configure("Title.TLabel", background=C["card"],
                     foreground=C["accent"], font=(FONT, 13, "bold"))
        s.configure("Section.TLabel", background=C["bg"],
                     foreground=C["accent"], font=(FONT, 14, "bold"))
        s.configure("Big.TLabel", background=C["card"], foreground=C["text"],
                     font=(FONT, 22, "bold"))
        s.configure("Status.TLabel", background=C["card"], font=(FONT, 11))

        # buttons
        s.configure("Accent.TButton", background=C["btn"], foreground=C["bg"],
                     font=(FONT, 11, "bold"), padding=(16, 6))
        s.map("Accent.TButton",
               background=[("active", C["btn_act"]),
                           ("disabled", C["btn_dis"])],
               foreground=[("disabled", C["dim"])])

        s.configure("Flat.TButton", background=C["card"],
                     foreground=C["text"], font=(FONT, 9), padding=(10, 4),
                     borderwidth=0)
        s.map("Flat.TButton",
               background=[("active", C["border"])],
               foreground=[("active", C["text"])])

        # entry
        s.configure("TEntry", fieldbackground=C["entry"],
                     foreground=C["text"], insertcolor=C["text"],
                     borderwidth=1, relief="flat")

        # combobox
        s.configure("TCombobox", fieldbackground=C["entry"],
                     background=C["card"], foreground=C["text"],
                     arrowcolor=C["accent"], borderwidth=1, relief="flat")
        s.map("TCombobox",
               fieldbackground=[("readonly", C["entry"])],
               foreground=[("readonly", C["text"])],
               arrowcolor=[("readonly", C["accent"])])

        # checkbutton
        s.configure("TCheckbutton", background=C["card"],
                     foreground=C["text"], font=(FONT, 10))
        s.map("TCheckbutton",
               indicatorcolor=[("selected", C["accent"]),
                               ("!selected", C["entry"])])

        # scrollbar
        s.configure("Vertical.TScrollbar", background=C["border"],
                     troughcolor=C["bg"], borderwidth=0, arrowsize=12)
        s.map("Vertical.TScrollbar",
               background=[("active", C["accent_dm"])])

    def _create_variables(self):
        self.url_var = tk.StringVar(value="https://example.com/")
        self.browser_var = tk.StringVar(value="chromium")
        self.headless_var = tk.BooleanVar(value=True)
        self.timeout_var = tk.StringVar(value="30")

    # ── 建構 UI ──────────────────────────────────────────────

    def _build_ui(self):
        # header
        hdr = ttk.Frame(self.root)
        hdr.pack(fill=tk.X, padx=20, pady=(14, 6))
        ttk.Label(hdr, text="網站健康檢查工具",
                   font=(FONT, 16, "bold"),
                   foreground=C["accent"], background=C["bg"]).pack(side=tk.LEFT)

        # main: left + right
        body = ttk.Frame(self.root)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 6))

        self._build_left(body)
        self._build_right(body)

        # log
        self._build_log()

        # button bar
        self._build_bar()

    # ── 左側面板 ─────────────────────────────────────────────

    def _build_left(self, parent):
        wrap = tk.Frame(parent, bg=C["bg"], width=340)
        wrap.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        wrap.pack_propagate(False)

        card = tk.Frame(wrap, bg=C["card"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        # title
        tk.Label(card, text="檢查設定", bg=C["card"], fg=C["accent"],
                 font=(FONT, 13, "bold")).pack(anchor=tk.W, padx=16,
                                                pady=(16, 10))

        # URL
        tk.Label(card, text="網址", bg=C["card"], fg=C["dim"],
                 font=(FONT, 9)).pack(anchor=tk.W, padx=16)
        self.url_entry = ttk.Entry(card, textvariable=self.url_var, width=38)
        self.url_entry.pack(padx=16, pady=(2, 12), fill=tk.X)

        # browser
        tk.Label(card, text="瀏覽器", bg=C["card"], fg=C["dim"],
                 font=(FONT, 9)).pack(anchor=tk.W, padx=16)
        self.browser_cb = ttk.Combobox(
            card, textvariable=self.browser_var,
            values=list(BROWSERS), state="readonly", width=36)
        self.browser_cb.pack(padx=16, pady=(2, 12), fill=tk.X)

        # headless
        ttk.Checkbutton(card, text="無頭模式 (headless)",
                         variable=self.headless_var).pack(
            anchor=tk.W, padx=16, pady=(0, 12))

        # timeout
        tk.Label(card, text="超時時間 (秒)", bg=C["card"], fg=C["dim"],
                 font=(FONT, 9)).pack(anchor=tk.W, padx=16)
        self.timeout_entry = ttk.Entry(
            card, textvariable=self.timeout_var, width=38)
        self.timeout_entry.pack(padx=16, pady=(2, 16), fill=tk.X)

        # start button
        self.start_btn = ttk.Button(
            card, text="開始檢查", style="Accent.TButton",
            command=self._start_check)
        self.start_btn.pack(padx=16, pady=(0, 16), fill=tk.X)

    # ── 右側面板 ─────────────────────────────────────────────

    def _build_right(self, parent):
        wrap = tk.Frame(parent, bg=C["bg"])
        wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        card = tk.Frame(wrap, bg=C["card"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text="檢查結果", bg=C["card"], fg=C["accent"],
                 font=(FONT, 13, "bold")).pack(anchor=tk.W, padx=16,
                                                pady=(16, 6))

        # ─ status cards row ─
        row = tk.Frame(card, bg=C["card"])
        row.pack(fill=tk.X, padx=16, pady=(4, 8))

        # HTTP status card
        self.http_frame = tk.Frame(row, bg=C["entry"],
                                    highlightbackground=C["border"],
                                    highlightthickness=1)
        self.http_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                              padx=(0, 6))
        tk.Label(self.http_frame, text="HTTP 狀態", bg=C["entry"],
                 fg=C["dim"], font=(FONT, 8)).pack(anchor=tk.W, padx=10,
                                                     pady=(6, 0))
        self.http_lbl = tk.Label(self.http_frame, text="--", bg=C["entry"],
                                  fg=C["text"], font=(FONT, 20, "bold"))
        self.http_lbl.pack(anchor=tk.W, padx=10, pady=(0, 8))

        # response time card
        self.time_frame = tk.Frame(row, bg=C["entry"],
                                    highlightbackground=C["border"],
                                    highlightthickness=1)
        self.time_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                              padx=(6, 0))
        tk.Label(self.time_frame, text="回應時間", bg=C["entry"],
                 fg=C["dim"], font=(FONT, 8)).pack(anchor=tk.W, padx=10,
                                                     pady=(6, 0))
        self.time_lbl = tk.Label(self.time_frame, text="--", bg=C["entry"],
                                  fg=C["text"], font=(FONT, 20, "bold"))
        self.time_lbl.pack(anchor=tk.W, padx=10, pady=(0, 8))

        # ─ title ─
        self._make_field(card, "頁面標題", "title_val")

        # ─ final url ─
        self._make_field(card, "最終網址", "final_url_val")

        # ─ overall status ─
        self.status_lbl = tk.Label(card, text="尚未檢查", bg=C["card"],
                                    fg=C["dim"], font=(FONT, 12, "bold"))
        self.status_lbl.pack(anchor=tk.W, padx=16, pady=(10, 4))

        # ─ screenshot preview ─
        tk.Label(card, text="截圖預覽", bg=C["card"], fg=C["dim"],
                 font=(FONT, 9)).pack(anchor=tk.W, padx=16, pady=(6, 2))

        preview_outer = tk.Frame(card, bg=C["entry"],
                                  highlightbackground=C["border"],
                                  highlightthickness=1)
        preview_outer.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        self.preview_lbl = tk.Label(preview_outer, bg=C["entry"],
                                     fg=C["dim"], text="暫無截圖",
                                     font=(FONT, 10))
        self.preview_lbl.pack(fill=tk.BOTH, expand=True)

    def _make_field(self, parent, label, attr_name):
        """建立一個標題 + 值的欄位區塊。"""
        frame = tk.Frame(parent, bg=C["card"])
        frame.pack(fill=tk.X, padx=16, pady=(6, 2))
        tk.Label(frame, text=label, bg=C["card"], fg=C["dim"],
                 font=(FONT, 9)).pack(anchor=tk.W)
        val_lbl = tk.Label(frame, text="--", bg=C["card"], fg=C["text"],
                            font=(FONT, 10), wraplength=500, justify=tk.LEFT)
        val_lbl.pack(anchor=tk.W)
        setattr(self, attr_name, val_lbl)

    # ── 日誌區 ───────────────────────────────────────────────

    def _build_log(self):
        wrap = ttk.Frame(self.root)
        wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 6))

        ttk.Label(wrap, text="執行日誌",
                   style="Section.TLabel").pack(anchor=tk.W, pady=(0, 4))

        inner = tk.Frame(wrap, bg=C["log"],
                         highlightbackground=C["border"],
                         highlightthickness=1)
        inner.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            inner, bg=C["log"], fg=C["text"], insertbackground=C["text"],
            font=(MONO, 9), wrap=tk.WORD, state=tk.DISABLED,
            borderwidth=0, highlightthickness=0)
        scroll = ttk.Scrollbar(inner, command=self.log_text.yview,
                                orient=tk.VERTICAL)
        self.log_text.configure(yscrollcommand=scroll.set)

        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ── 底部按鈕列 ───────────────────────────────────────────

    def _build_bar(self):
        bar = tk.Frame(self.root, bg=C["bg"])
        bar.pack(fill=tk.X, padx=20, pady=(0, 12))

        for text, cmd in [
            ("開啟輸出資料夾", lambda: _open_folder(OUTPUT_DIR)),
            ("清除結果", self._clear_results),
            ("歷史紀錄", self._show_history),
            ("清除紀錄", self._clear_history_action),
        ]:
            ttk.Button(bar, text=text, style="Flat.TButton",
                        command=cmd).pack(side=tk.LEFT, padx=(0, 8))

    # ── 動作 ─────────────────────────────────────────────────

    def _start_check(self):
        if self._checking:
            return

        # validate URL
        url_err = validate_url(self.url_var.get())
        if url_err:
            messagebox.showwarning("輸入錯誤", url_err)
            return

        # validate timeout
        timeout, t_err = validate_timeout(self.timeout_var.get())
        if t_err:
            messagebox.showwarning("輸入錯誤", t_err)
            return

        self._checking = True
        self.start_btn.config(state=tk.DISABLED)
        self._clear_results()

        url = self.url_var.get().strip()
        browser = self.browser_var.get()
        headless = self.headless_var.get()

        threading.Thread(
            target=self._worker,
            args=(url, browser, headless, timeout),
            daemon=True,
        ).start()

    def _worker(self, url, browser_name, headless, timeout):
        """Background worker — runs Playwright off the main thread."""

        def log_cb(msg):
            self.root.after(0, self._append_log, msg)

        result = check_url(url, browser_name, headless, timeout, log_cb)

        # persist history (only in GUI mode)
        try:
            save_check(result)
        except Exception:
            pass

        self.root.after(0, self._on_check_done, result)

    def _on_check_done(self, result):
        self._checking = False
        self.start_btn.config(state=tk.NORMAL)
        self._display_results(result)

    # ── 結果顯示 ─────────────────────────────────────────────

    def _display_results(self, r):
        self.http_lbl.config(text=str(r["status"]) if r["status"] else "--")
        if r["response_time"] is not None:
            self.time_lbl.config(text=f"{r['response_time']:.3f}s")
        self.title_val.config(text=r["title"] or "--")
        self.final_url_val.config(text=r["final_url"] or "--")

        # colour-code HTTP status
        status = r["status"]
        if status and 200 <= status < 300:
            self.http_lbl.config(fg=C["ok"])
        elif status and 300 <= status < 400:
            self.http_lbl.config(fg=C["warn"])
        elif status:
            self.http_lbl.config(fg=C["err"])
        else:
            self.http_lbl.config(fg=C["dim"])

        # overall status
        if r["success"]:
            self.status_lbl.config(text="✓ 正常運作", fg=C["ok"])
        else:
            self.status_lbl.config(text=f"✗ {r['error']}", fg=C["err"])

        # screenshot
        self._load_screenshot(r.get("screenshot_path", ""))

    def _load_screenshot(self, path: str):
        if not path or not Path(path).exists():
            self.preview_lbl.config(image="", text="暫無截圖")
            self.preview_lbl.image = None
            return
        if not HAS_PIL:
            self.preview_lbl.config(
                image="",
                text=f"截圖已儲存: {Path(path).name}\n(安裝 Pillow 可預覽)")
            return
        try:
            img = Image.open(path)
            max_w, max_h = 420, 260
            ratio = min(max_w / img.width, max_h / img.height, 1.0)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.preview_lbl.config(image=photo, text="")
            self.preview_lbl.image = photo  # prevent GC
        except Exception:
            self.preview_lbl.config(image="", text="截圖載入失敗")

    # ── 日誌 ─────────────────────────────────────────────────

    def _append_log(self, msg):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    # ── 清除 ─────────────────────────────────────────────────

    def _clear_results(self):
        self.http_lbl.config(text="--", fg=C["text"])
        self.time_lbl.config(text="--")
        self.title_val.config(text="--")
        self.final_url_val.config(text="--")
        self.status_lbl.config(text="尚未檢查", fg=C["dim"])
        self.preview_lbl.config(image="", text="暫無截圖")
        self.preview_lbl.image = None

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    # ── 歷史紀錄 ─────────────────────────────────────────────

    def _show_history(self):
        win = tk.Toplevel(self.root)
        win.title("歷史紀錄")
        win.geometry("860x480")
        win.configure(bg=C["bg"])

        cols = ("time", "url", "browser", "status", "resp", "result")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=18)
        headings = {
            "time": ("時間", 150), "url": ("網址", 260),
            "browser": ("瀏覽器", 80), "status": ("狀態碼", 70),
            "resp": ("回應時間", 80), "result": ("結果", 60),
        }
        for cid, (text, w) in headings.items():
            tree.heading(cid, text=text)
            tree.column(cid, width=w, anchor=tk.CENTER)
        tree.column("url", anchor=tk.W)

        for rec in get_history():
            tree.insert("", tk.END, values=(
                rec["checked_at"] or "",
                rec["url"],
                rec["browser"],
                rec["status"] or "N/A",
                f"{rec['response_time']:.3f}s" if rec["response_time"] else "N/A",
                "OK" if rec["success"] else "FAIL",
            ))

        tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    def _clear_history_action(self):
        if messagebox.askyesno("確認", "確定要清除所有歷史紀錄嗎？"):
            clear_history()
            messagebox.showinfo("完成", "歷史紀錄已清除")

    # ── 關閉 ─────────────────────────────────────────────────

    def _on_closing(self):
        if self._checking:
            if messagebox.askyesno("確認", "正在進行檢查中，確定要關閉嗎？"):
                self.root.destroy()
        else:
            self.root.destroy()


# ══════════════════════════════════════════════════════════════
#  程式入口
# ══════════════════════════════════════════════════════════════


def main():
    root = tk.Tk()
    HealthCheckApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
