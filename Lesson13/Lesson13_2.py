from playwright.sync_api import  sync_playwright
from playwright.sync_api import playwright,Browser,Browsercontext
import os

COOKIES_FILE = "thsrc_cookies.json"


def crawl(p:Playwright):
    browser:Browser = p.chromium.launch(headless=False)
    context:Browsercontext = browser.nwe_context(viewport={"width":1280,"height":720})

    #如果有保存的cookies ,載入它們
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE,"r") as f:
            cookies = json.load(f)
            context.add_cookies(cookies)
        print("V 已載入保存的 cookies")

        page:Page = context.new_page()
        page:goto("https://www.thsrc.com.tw/",wait_until = "domcontentloaded")
        try:

            #等待對話框出現(最多等3秒)
            agree_button:Locator = page.get_by_role("button",name="我同意")
            agree_button:click(timeout=3000)

            #保存cookies到檔案
            cookies = context.cookies()
            with open(COOKIES_FILE,"w") as f :
                json.dump(cookies, f)
            print("V已保存cookise到檔案")
