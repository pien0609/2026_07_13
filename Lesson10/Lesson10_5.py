"""專案 01：開啟真實網頁，檢查標題並留下截圖。"""

import argparse

from checker import check_url


def check_website(browser_name: str = "chromium") -> None:
    """使用指定瀏覽器開啟網頁，檢查標題並截圖。"""
    def cli_log(msg):
        print(msg)

    result = check_url(
        url="https://example.com/",
        browser_name=browser_name,
        headless=True,
        log_callback=cli_log,
    )

    if result["success"]:
        print(f"\n瀏覽器: {result['browser']}")
        print(f"HTTP 狀態: {result['status']}")
        print(f"頁面標題: {result['title']}")
        print(f"主標題: {result['heading']}")
        print(f"截圖: {result['screenshot_path']}")
    else:
        print(f"\n檢查失敗: {result['error']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="網站健康檢查工具")
    parser.add_argument(
        "--browser", choices=["chromium", "firefox", "webkit"], default="chromium"
    )
    args = parser.parse_args()
    check_website(args.browser)
