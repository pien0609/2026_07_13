"""
Lesson11 - 維基百科爬蟲範例

使用 Playwright 自動化瀏覽器，前往中文維基百科搜尋指定關鍵字，
擷取搜尋結果的標題與摘要內容後輸出至終端機。

使用方式：
    pip install playwright
    playwright install
    python Lesson11_1.py
"""

import re
from datetime import datetime
from playwright.sync_api import sync_playwright, Playwright, Browser, Page


def launch_browser(p: Playwright) -> Browser:
    """啟動 Chromium 瀏覽器實例。

    Args:
        p: Playwright 啟動器物件，用於建立瀏覽器實例。

    Returns:
        啟動完成的 Chromium Browser 物件。
    """
    return p.chromium.launch()


def search_wikipedia(page: Page, keyword: str) -> None:
    """在中文維基百科搜尋指定關鍵字。

    步驟：
    1. 前往維基百科首頁
    2. 在搜尋框輸入關鍵字
    3. 截圖紀錄當前畫面（檔名含時間戳）
    4. 按下 Enter 送出搜尋
    5. 等待搜尋結果頁面載入完成

    Args:
        page: Playwright 的 Page 物件，代表一個瀏覽器分頁。
        keyword: 要搜尋的關鍵字。
    """
    # 前往維基百科首頁
    page.goto("https://zh.wikipedia.org")

    # 定位搜尋輸入框並填入關鍵字
    search_input = page.locator("#searchInput")
    search_input.fill(keyword)

    # 截圖保存，使用時間戳避免檔名衝突
    page.screenshot(path=f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

    # 送出搜尋
    search_input.press("Enter")

    # 等待搜尋結果頁面的標題元素出現，確保頁面載入完成
    page.wait_for_selector("#firstHeading")


def get_search_result(page: Page) -> dict[str, str]:
    """擷取搜尋結果頁面的標題與第一段摘要。

    會過濾掉空段落，因為中文維基百科的第一個 <p> 標籤
    常常是空段落或座標資訊，不具備參考價值。

    Args:
        page: 已載入搜尋結果的 Page 物件。

    Returns:
        包含 'heading'（標題）與 'content'（摘要，截取前 100 字元）的字典。
    """
    # 取得頁面標題
    heading: str = page.locator("#firstHeading").inner_text()

    # 取得所有段落，並過濾掉空段落（\S 表示非空白字元）
    paragraphs = page.locator("#mw-content-text p").filter(has_text=re.compile(r"\S"))

    # 取得第一個有內容的段落作為摘要，若無則回傳空字串
    content: str = paragraphs.first.inner_text() if paragraphs.count() > 0 else ""

    # 截取前 100 字元作為簡短摘要
    return {"heading": heading, "content": content[:100]}


def crawl(p: Playwright) -> None:
    """爬蟲主流程。

    完整流程：
    1. 啟動瀏覽器
    2. 在維基百科搜尋「臺灣」
    3. 擷取並印出搜尋結果的標題與摘要
    4. 返回維基百科首頁
    5. 關閉瀏覽器釋放資源

    Args:
        p: Playwright 啟動器物件。

    Raises:
        Exception: 爬蟲執行過程中的任何異常會被重新拋出。
    """
    browser: Browser = launch_browser(p)
    try:
        # 建立新的瀏覽器分頁
        page: Page = browser.new_page()

        # 在維基百科搜尋「臺灣」
        search_wikipedia(page, "臺灣")

        # 擷取搜尋結果並輸出
        result: dict[str, str] = get_search_result(page)
        print(f"搜尋主題: {result['heading']}")
        print(f"摘要: {result['content']}")

        # 返回首頁並驗證
        page.go_back()
        page.wait_for_selector("#searchInput")
        print(f"返回首頁: {page.title()}")
    except Exception as e:
        # 捕獲例外並印出錯誤訊息後重新拋出
        print(f"爬蟲執行失敗: {e}")
        raise
    finally:
        # 無論成功或失敗，都確保瀏覽器被關閉
        browser.close()


if __name__ == "__main__":
    # 使用 sync_playwright 上下文管理器啟動 Playwright
    with sync_playwright() as p:
        crawl(p)
