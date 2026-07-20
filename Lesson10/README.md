# 網站健康檢查工具

以 Python + Playwright + tkinter 打造的繁中 GUI 網站健康檢查 App。

## 檔案結構

| 檔案 | 說明 |
|------|------|
| `checker.py` | 核心檢查邏輯（可被 CLI / GUI 共用） |
| `gui.py` | tkinter GUI 入口 |
| `Lesson10_5.py` | CLI 入口（保留原有行為） |
| `requirements.txt` | 相依套件 |
| `tests/` | 單元測試 |

## 安裝

```bash
# 使用 uv（建議）
uv sync

# 或使用 pip
pip install -r requirements.txt

# 安裝 Playwright 瀏覽器
playwright install chromium
```

## 執行

```bash
# GUI 模式
uv run python gui.py
# 或
python gui.py

# CLI 模式
uv run python Lesson10_5.py --browser chromium
python Lesson10_5.py --browser firefox
```

## 測試

```bash
uv run pytest tests/ -v
```
