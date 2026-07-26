# Lesson11_1.py — Code Review

## 程式概述

使用 Playwright 自動化瀏覽器，在中文維基百科搜尋「臺灣」並擷取摘要內容。

---

## 優點

1. **結構清晰**：職責分離良好，每個函式只做一件事（SRP）。
2. **型別標註完整**：所有函式參數與回傳值都有型別提示，利於 IDE 與型別檢查工具。
3. **錯誤處理完善**：使用 `try/finally` 確保瀏覽器資源被正確釋放。
4. **docstring 規範**：每個函式都有完整的說明文件。

---

## 建議改進

### 1. 搜尋關鍵字應參數化

目前關鍵字 `"臺灣"` 為寫死的字串（hardcode），建議改為可配置。

```python
# 改進前
search_wikipedia(page, "臺灣")

# 改進後
def crawl(p: Playwright, keyword: str = "臺灣") -> None:
    ...
    search_wikipedia(page, keyword)
```

### 2. 截圖路徑應可配置

截圖目前存放在工作目錄下，檔名隨時間戳產生，建議：

- 使用 `pathlib.Path` 處理路徑
- 提供輸出目錄參數

```python
from pathlib import Path

def search_wikipedia(page: Page, keyword: str, screenshot_dir: Path = Path(".")) -> None:
    screenshot_path = screenshot_dir / f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"
    page.screenshot(path=str(screenshot_path))
```

### 3. 考慮加入 Retry 機制

網路請求容易因暫時性問題失敗，建議加入重試邏輯：

```python
from playwright.sync_api import TimeoutError as PlaywrightTimeout

MAX_RETRIES = 3

for attempt in range(1, MAX_RETRIES + 1):
    try:
        search_wikipedia(page, keyword)
        break
    except PlaywrightTimeout:
        if attempt == MAX_RETRIES:
            raise
        page.reload()
```

### 4. `get_search_result` 可能回傳空字串

`content[:100]` 若 `content` 為空，結果仍為空字串，呼叫端未處理此情況。

```python
result = get_search_result(page)
if not result["content"]:
    print("未擷取到摘要內容")
```

### 5. 缺少 logging 機制

目前使用 `print` 輸出，建議改用 `logging` 模組，方便調整輸出等級與格式：

```python
import logging

logger = logging.getLogger(__name__)

logger.info("搜尋主題: %s", result["heading"])
logger.error("爬蟲執行失敗: %s", e)
```

### 6. 考慮使用 `headless` 參數

目前 `p.chromium.launch()` 預設為 headless 模式，建議明確指定並提供選項：

```python
def launch_browser(p: Playwright, headless: bool = True) -> Browser:
    return p.chromium.launch(headless=headless)
```

### 7. 常數可集中管理

維基百科 URL 與截取字元數等魔法數字（magic number）建議抽為常數：

```python
WIKIPEDIA_URL = "https://zh.wikipedia.org"
MAX_SUMMARY_LENGTH = 100
```

---

## 總結

| 項目 | 評分 |
|------|------|
| 可讀性 | ⭐⭐⭐⭐⭐ |
| 結構設計 | ⭐⭐⭐⭐ |
| 錯誤處理 | ⭐⭐⭐⭐ |
| 可擴展性 | ⭐⭐⭐ |
| 可維護性 | ⭐⭐⭐⭐ |

整體而言，這是一個結構良好的爬蟲範例程式，主要改進方向為**參數化**、**可配置性**以及**錯誤恢復機制**。
