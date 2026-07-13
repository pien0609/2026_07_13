import random
import tkinter as tk
from tkinter import messagebox, font as tkfont


class NumberGuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("猜數字遊戲")
        self.root.resizable(False, False)

        # ---------- 遊戲狀態 ----------
        self.target = 0
        self.low = 1
        self.high = 100
        self.attempts = 0
        self.history = []

        # ---------- 色彩主題 ----------
        self.COLORS = {
            "bg": "#1a1a2e",
            "card": "#16213e",
            "accent": "#e94560",
            "success": "#0f9b58",
            "text": "#eaeaea",
            "text_dim": "#8899aa",
            "input_bg": "#0f3460",
            "btn": "#e94560",
            "btn_hover": "#c73e54",
            "high": "#ff6b6b",
            "low": "#4ecdc4",
            "history_bg": "#0f3460",
        }

        self.root.configure(bg=self.COLORS["bg"])

        # ---------- 字型 ----------
        self.title_font = tkfont.Font(family="Microsoft JhengHei", size=22, weight="bold")
        self.label_font = tkfont.Font(family="Microsoft JhengHei", size=12)
        self.big_font = tkfont.Font(family="Microsoft JhengHei", size=28, weight="bold")
        self.small_font = tkfont.Font(family="Microsoft JhengHei", size=10)
        self.history_font = tkfont.Font(family="Consolas", size=10)

        self._build_ui()
        self.new_game()

    # ==================== UI 建構 ====================
    def _build_ui(self):
        # 標題
        tk.Label(
            self.root, text="猜數字遊戲", font=self.title_font,
            bg=self.COLORS["bg"], fg=self.COLORS["accent"],
        ).pack(pady=(18, 2))

        tk.Label(
            self.root, text="在範圍內猜出隨機數字！", font=self.small_font,
            bg=self.COLORS["bg"], fg=self.COLORS["text_dim"],
        ).pack(pady=(0, 10))

        # ---- 主卡片 ----
        card = tk.Frame(self.root, bg=self.COLORS["card"], bd=0, relief="flat")
        card.pack(padx=20, pady=5, fill="x")

        # 範圍顯示
        self.range_label = tk.Label(
            card, text="", font=self.label_font,
            bg=self.COLORS["card"], fg=self.COLORS["text_dim"],
        )
        self.range_label.pack(pady=(14, 2))

        # 提示訊息
        self.hint_label = tk.Label(
            card, text="請輸入你的猜測", font=self.big_font,
            bg=self.COLORS["card"], fg=self.COLORS["text"],
        )
        self.hint_label.pack(pady=(6, 10))

        # 輸入欄 + 送出按鈕
        input_frame = tk.Frame(card, bg=self.COLORS["card"])
        input_frame.pack(pady=(0, 6))

        self.entry = tk.Entry(
            input_frame, width=12, font=self.big_font,
            bg=self.COLORS["input_bg"], fg="white",
            insertbackground="white", relief="flat",
            justify="center",
        )
        self.entry.pack(side="left", padx=(0, 8), ipady=4)
        self.entry.bind("<Return>", lambda e: self._on_guess())

        self.guess_btn = tk.Button(
            input_frame, text="猜！", font=self.label_font,
            bg=self.COLORS["btn"], fg="white",
            activebackground=self.COLORS["btn_hover"],
            activeforeground="white", relief="flat",
            cursor="hand2", width=6, height=1,
            command=self._on_guess,
        )
        self.guess_btn.pack(side="left", ipady=2)

        # 猜測次數
        self.attempts_label = tk.Label(
            card, text="已猜測：0 次", font=self.small_font,
            bg=self.COLORS["card"], fg=self.COLORS["text_dim"],
        )
        self.attempts_label.pack(pady=(2, 10))

        # ---- 猜測歷史 ----
        tk.Label(
            self.root, text="猜測紀錄", font=self.small_font,
            bg=self.COLORS["bg"], fg=self.COLORS["text_dim"],
        ).pack(anchor="w", padx=28, pady=(10, 0))

        history_frame = tk.Frame(self.root, bg=self.COLORS["history_bg"])
        history_frame.pack(padx=20, pady=(4, 10), fill="both")

        self.history_listbox = tk.Listbox(
            history_frame, height=6, font=self.history_font,
            bg=self.COLORS["history_bg"], fg=self.COLORS["text"],
            selectbackground=self.COLORS["history_bg"],
            selectforeground=self.COLORS["text"],
            relief="flat", highlightthickness=0, bd=0,
        )
        self.history_listbox.pack(fill="both", padx=2, pady=2)

        # ---- 按鈕列 ----
        btn_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        btn_frame.pack(pady=(4, 16))

        self.new_game_btn = tk.Button(
            btn_frame, text="新遊戲", font=self.label_font,
            bg=self.COLORS["input_bg"], fg="white",
            activebackground="#1a4a7a", activeforeground="white",
            relief="flat", cursor="hand2", width=14,
            command=self.new_game,
        )
        self.new_game_btn.pack(side="left", padx=6)

        self.quit_btn = tk.Button(
            btn_frame, text="離開", font=self.label_font,
            bg="#444", fg="white",
            activebackground="#666", activeforeground="white",
            relief="flat", cursor="hand2", width=8,
            command=self.root.destroy,
        )
        self.quit_btn.pack(side="left", padx=6)

        self.entry.focus_set()

    # ==================== 遊戲邏輯 ====================
    def new_game(self):
        self.target = random.randint(1, 100)
        self.low = 1
        self.high = 100
        self.attempts = 0
        self.history.clear()

        self.hint_label.config(text="?", fg=self.COLORS["text"])
        self._update_range()
        self._update_attempts()
        self.history_listbox.delete(0, tk.END)
        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        self.guess_btn.config(state="normal")
        self.entry.focus_set()

    def _on_guess(self):
        raw = self.entry.get().strip()
        if not raw:
            return

        try:
            guess = int(raw)
        except ValueError:
            messagebox.showwarning("輸入錯誤", "請輸入一個整數！")
            return

        if guess < self.low or guess > self.high:
            messagebox.showwarning("超出範圍", f"請輸入 {self.low} ~ {self.high} 之間的數字！")
            return

        self.attempts += 1
        self.entry.delete(0, tk.END)

        if guess == self.target:
            self._win(guess)
        elif guess < self.target:
            self.low = guess + 1
            self._record(guess, "偏小", self.COLORS["low"])
            self.hint_label.config(text="再大一點！", fg=self.COLORS["low"])
        else:
            self.high = guess - 1
            self._record(guess, "偏大", self.COLORS["high"])
            self.hint_label.config(text="再小一點！", fg=self.COLORS["high"])

        self._update_range()
        self._update_attempts()

    def _win(self, guess):
        self.history.append((guess, "正確"))
        self.history_listbox.insert(tk.END, f"  {guess}  ✔  正確！")
        self.history_listbox.itemconfig(tk.END, fg=self.COLORS["success"])

        stars = "★" * min(self.attempts, 10)
        self.hint_label.config(
            text=f"恭喜答對！{self.target}",
            fg=self.COLORS["success"],
        )
        self.attempts_label.config(text=f"共猜了 {self.attempts} 次  {stars}")
        self.entry.config(state="disabled")
        self.guess_btn.config(state="disabled")

        messagebox.showinfo(
            "答對了！",
            f"答案就是 {self.target}\n你總共猜了 {self.attempts} 次！",
        )

    def _record(self, guess, label, color):
        entry = f"  {guess}  →  {label}（範圍 {self.low} ~ {self.high}）"
        self.history.append((guess, label))
        self.history_listbox.insert(tk.END, entry)
        self.history_listbox.itemconfig(tk.END, fg=color)
        self.history_listbox.see(tk.END)

    def _update_range(self):
        self.range_label.config(text=f"範圍：{self.low} ~ {self.high}")

    def _update_attempts(self):
        self.attempts_label.config(text=f"已猜測：{self.attempts} 次")


# ==================== 啟動 ====================
if __name__ == "__main__":
    root = tk.Tk()
    NumberGuessingGame(root)
    root.mainloop()
