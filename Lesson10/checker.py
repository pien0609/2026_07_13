"""網站健康檢查核心模組。

提供可被 CLI 與 GUI 共用的檢查邏輯，以及 SQLite 歷史紀錄功能。
"""

import sqlite3
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, Error as PlaywrightError

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
DB_PATH = Path(__file__).resolve().parent / "history.db"
BROWSERS = ("chromium", "firefox", "webkit")


# ── 輸入驗證 ──────────────────────────────────────────────────


def validate_url(url: str) -> str | None:
    """驗證網址格式，回傳錯誤訊息或 None。"""
    if not url or not url.strip():
        return "請輸入網址"
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return "網址必須以 http:// 或 https:// 開頭"
    if not parsed.netloc:
        return "網址格式不正確，請輸入完整的網域名稱（如 https://example.com）"
    return None


def validate_timeout(value: str) -> tuple[int | None, str | None]:
    """驗證超時參數，回傳 (整數值, 錯誤訊息)。"""
    try:
        timeout = int(value)
    except (ValueError, TypeError):
        return None, "超時時間必須是整數"
    if timeout < 1:
        return None, "超時時間不能小於 1 秒"
    if timeout > 300:
        return None, "超時時間不能超過 300 秒"
    return timeout, None


# ── 核心檢查函式 ──────────────────────────────────────────────


def check_url(
    url: str,
    browser_name: str = "chromium",
    headless: bool = True,
    timeout: int = 30,
    log_callback=None,
) -> dict:
    """檢查指定網址的健康狀態，回傳結果字典。

    Parameters
    ----------
    url : str
        目標網址。
    browser_name : str
        瀏覽器名稱（chromium / firefox / webkit）。
    headless : bool
        是否以無頭模式執行。
    timeout : int
        逾時秒數。
    log_callback : callable | None
        日誌回呼函式，接受一個 str 參數。

    Returns
    -------
    dict
        包含 url, final_url, status, response_time, title,
        heading, screenshot_path, browser, success, error。
    """
    result = {
        "url": url,
        "final_url": "",
        "status": None,
        "response_time": None,
        "title": "",
        "heading": "",
        "screenshot_path": "",
        "browser": browser_name,
        "success": False,
        "error": None,
    }

    def log(msg):
        if log_callback:
            log_callback(msg)

    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
        log(f"正在啟動 {browser_name} 瀏覽器…")

        with sync_playwright() as pw:
            browser_type = getattr(pw, browser_name)
            browser = browser_type.launch(headless=headless)
            page = browser.new_page(viewport={"width": 1280, "height": 720})

            log(f"正在前往 {url} …")
            start_time = time.time()
            response = page.goto(
                url, wait_until="domcontentloaded", timeout=timeout * 1000
            )
            elapsed = time.time() - start_time

            result["response_time"] = round(elapsed, 3)
            result["status"] = response.status if response else None
            result["final_url"] = page.url
            result["title"] = page.title()

            log(f"HTTP {result['status']} — 耗時 {elapsed:.2f}s")

            try:
                heading_el = page.get_by_role("heading").first
                result["heading"] = heading_el.inner_text(timeout=3000)
            except Exception:
                result["heading"] = ""

            screenshot = OUTPUT_DIR / f"homepage_{browser_name}.png"
            page.screenshot(path=screenshot, full_page=True)
            result["screenshot_path"] = str(screenshot)
            log(f"截圖已儲存: {screenshot}")

            browser.close()

        result["success"] = True
        log("檢查完成 ✓")

    except PlaywrightError as e:
        error_msg = str(e)
        if "Executable doesn't exist" in error_msg:
            result["error"] = (
                f"瀏覽器尚未安裝，請先執行：playwright install {browser_name}"
            )
        elif "Timeout" in error_msg or "timeout" in error_msg.lower():
            result["error"] = (
                f"連線逾時（{timeout}s），請確認網址是否正確或增加超時時間"
            )
        elif "ERR_NAME_NOT_RESOLVED" in error_msg:
            result["error"] = "無法解析網域名稱，請檢查網址是否正確"
        elif "ERR_CERT" in error_msg or "SSL" in error_msg.upper():
            result["error"] = "SSL 憑證錯誤，請確認網址是否正確"
        elif "ERR_CONNECTION" in error_msg:
            result["error"] = "無法連線到目標網站，請確認網路是否正常"
        else:
            result["error"] = f"瀏覽器錯誤: {e}"
        log(f"✗ {result['error']}")
    except Exception as e:
        result["error"] = f"發生未預期的錯誤: {e}"
        log(f"✗ {result['error']}")

    return result


# ── SQLite 歷史紀錄 ──────────────────────────────────────────


def _get_db() -> sqlite3.Connection:
    """取得或建立資料庫連線。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS checks (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            url           TEXT    NOT NULL,
            browser       TEXT    NOT NULL,
            status        INTEGER,
            response_time REAL,
            title         TEXT,
            final_url     TEXT,
            success       INTEGER,
            error         TEXT,
            checked_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


def save_check(result: dict) -> None:
    """將檢查結果存入 SQLite。"""
    conn = _get_db()
    conn.execute(
        """INSERT INTO checks
           (url, browser, status, response_time, title,
            final_url, success, error)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            result["url"],
            result["browser"],
            result["status"],
            result["response_time"],
            result["title"],
            result["final_url"],
            int(result["success"]),
            result["error"],
        ),
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 100) -> list[dict]:
    """取得最近的檢查紀錄。"""
    conn = _get_db()
    rows = conn.execute(
        """SELECT url, browser, status, response_time, title,
                  final_url, success, error, checked_at
           FROM checks ORDER BY id DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [
        {
            "url": r[0],
            "browser": r[1],
            "status": r[2],
            "response_time": r[3],
            "title": r[4],
            "final_url": r[5],
            "success": bool(r[6]),
            "error": r[7],
            "checked_at": r[8],
        }
        for r in rows
    ]


def clear_history() -> None:
    """清除所有歷史紀錄。"""
    conn = _get_db()
    conn.execute("DELETE FROM checks")
    conn.commit()
    conn.close()
