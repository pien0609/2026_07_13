from playwright.sync_api import sync_playwright, Browser, Page
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(
            headless=False,
            slow_mo=300
        )
        page: Page = browser.new_page()
        page.set_default_timeout(60000)

        print("前往台灣高鐵訂票系統...")
        page.goto("https://irs.thsrc.com.tw/IMINT/?locale=tw", wait_until="load", timeout=60000)
        time.sleep(3)

        # 點掉 Cookie 同意
        try:
            page.locator("button:has-text('我同意')").click(timeout=3000)
            print("已關閉 Cookie 通知")
            time.sleep(1)
        except:
            pass

        # 1. 單程
        page.locator("select[name='tripCon:typesoftrip']").select_option("0")
        print("1. 單程")

        # 2. 出發站 = 台北
        page.locator("select[name='selectStartStation']").select_option("2")
        print("2. 出發站: 台北")

        # 3. 到達站 = 台中
        page.locator("select[name='selectDestinationStation']").select_option("7")
        print("3. 到達站: 台中")

        # 4. 日期 2026/07/29
        page.evaluate("""
            var inputs = document.querySelectorAll('input[type="text"]');
            for (var i = 0; i < inputs.length; i++) {
                if (inputs[i].classList.contains('uk-input')) {
                    inputs[i].value = '2026/07/29';
                }
            }
            var hiddenInput = document.querySelector('input[name="toTimeInputField"]');
            if (hiddenInput) hiddenInput.value = '2026/07/29';
        """)
        print("4. 日期: 2026/07/29")

        # 5. 出發時間 = 19:00
        page.locator("select[name='toTimeTable']").select_option("700P")
        print("5. 時間: 19:00")

        # 6. 全票 1 張
        page.locator("select[name='ticketPanel:rows:0:ticketAmount']").select_option("1")
        print("6. 全票: 1 張")

        time.sleep(1)

        print("\n=== 已自動填入所有訂票資訊 ===")
        print("請在瀏覽器中輸入驗證碼後手動查詢\n")
        print("按 Ctrl+C 或在此視窗按 Enter 關閉瀏覽器...")

        try:
            input()
        except:
            pass

        browser.close()

if __name__ == "__main__":
    main()
