from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PwTimeoutError
from pathlib import Path
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = Path(__file__).parent


def accept_cookies(page: Page) -> None:
    try:
        page.locator("button:has-text('我同意')").click(timeout=5000)
        print("1. 已關閉 Cookie 通知")
    except PwTimeoutError:
        print("1. 無 Cookie 通知")


def fill_station(page: Page, select_name: str, station_name: str, step_label: str) -> None:
    select = page.locator(f"select[name='{select_name}']")
    select.select_option(label=station_name)
    print(f"{step_label} {station_name}")


def fill_date(page: Page, date_str: str) -> None:
    page.evaluate("""
        (dateStr) => {
            const inputs = document.querySelectorAll('input[type="text"]');
            for (const inp of inputs) {
                if (inp.classList.contains('uk-input')) {
                    inp.value = dateStr;
                }
            }
            const hidden = document.querySelector('input[name="toTimeInputField"]');
            if (hidden) hidden.value = dateStr;
        }
    """, date_str)
    result = page.evaluate("document.querySelector('input[name=\"toTimeInputField\"]')?.value")
    assert result == date_str, f"日期設定失敗：預期 {date_str}，實際 {result}"
    print(f"3. 日期: {date_str}")


def fill_time(page: Page, select_name: str, time_value: str, time_label: str) -> None:
    page.locator(f"select[name='{select_name}']").select_option(time_value)
    print(f"4. 時間: {time_label}")


def fill_ticket(page: Page, row: int, amount: str) -> None:
    page.locator(f"select[name='ticketPanel:rows:{row}:ticketAmount']").select_option(amount)
    print(f"5. {['全票', '孩童票', '愛心票', '敬老票', '大學生票', '少年票'][row]}: {amount} 張")


def main() -> None:
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=False, slow_mo=300)
        page: Page = browser.new_page()
        page.set_default_timeout(30000)

        print("前往台灣高鐵訂票系統...")
        page.goto(
            "https://irs.thsrc.com.tw/IMINT/?locale=tw",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_load_state("load")
        page.wait_for_selector("select[name='selectStartStation']", timeout=15000)
        print("頁面載入完成")

        accept_cookies(page)

        # 單程
        page.locator("select[name='tripCon:typesoftrip']").select_option(label="單程")
        print("2. 行程: 單程")

        # 出發站 / 到達站
        fill_station(page, "selectStartStation", "台北", "  出發站:")
        fill_station(page, "selectDestinationStation", "台中", "  到達站:")

        # 日期
        fill_date(page, "2026/07/29")

        # 出發時間 19:00
        fill_time(page, "toTimeTable", "700P", "19:00")

        # 全票 1 張
        fill_ticket(page, 0, "1")

        print("\n=== 已自動填入所有訂票資訊 ===")
        print("請在瀏覽器中輸入驗證碼後手動查詢")
        print("關閉請按 Enter...", end=" ", flush=True)
        input()

        browser.close()


if __name__ == "__main__":
    main()
