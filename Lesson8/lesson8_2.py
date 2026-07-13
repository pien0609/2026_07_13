import random
import tkinter as tk
from tkinter import messagebox

def new_game():
    global target, low, high, attempts
    target = random.randint(1, 100)
    low, high = 1, 100
    attempts = 0
    update_range_label()
    entry.delete(0, tk.END)
    result_label.config(text="")
    attempts_label.config(text="已猜次數：0")
    entry.config(state="normal")
    guess_button.config(state="normal")

def update_range_label():
    range_label.config(text=f"請猜一個 {low} ~ {high} 之間的數字")

def make_guess():
    global low, high, attempts
    try:
        guess = int(entry.get())
    except ValueError:
        messagebox.showwarning("輸入錯誤", "請輸入有效數字！")
        return

    if guess < low or guess > high:
        messagebox.showwarning("超出範圍", f"請輸入 {low} ~ {high} 之間的數字！")
        return

    attempts += 1
    attempts_label.config(text=f"已猜次數：{attempts}")

    if guess == target:
        result_label.config(text=f"恭喜你猜中了！答案就是 {target}", fg="green")
        entry.config(state="disabled")
        guess_button.config(state="disabled")
    elif guess < target:
        result_label.config(text="太小了！", fg="blue")
        low = guess + 1
    else:
        result_label.config(text="太大了！", fg="red")
        high = guess - 1

    update_range_label()
    entry.delete(0, tk.END)

root = tk.Tk()
root.title("猜數字遊戲")
root.resizable(False, False)

target = random.randint(1, 100)
low, high = 1, 100
attempts = 0

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Label(frame, text="猜數字遊戲", font=("Arial", 20, "bold")).pack(pady=(0, 10))
range_label = tk.Label(frame, text="", font=("Arial", 12))
range_label.pack()

input_frame = tk.Frame(frame)
input_frame.pack(pady=10)

entry = tk.Entry(input_frame, font=("Arial", 14), width=10, justify="center")
entry.pack(side="left", padx=(0, 10))
entry.bind("<Return>", lambda event: make_guess())

guess_button = tk.Button(input_frame, text="猜！", font=("Arial", 12), command=make_guess)
guess_button.pack(side="left")

result_label = tk.Label(frame, text="", font=("Arial", 14, "bold"))
result_label.pack(pady=5)

attempts_label = tk.Label(frame, text="已猜次數：0", font=("Arial", 11))
attempts_label.pack()

tk.Button(frame, text="重新開始", font=("Arial", 11), command=new_game).pack(pady=(10, 0))

update_range_label()

root.mainloop()
