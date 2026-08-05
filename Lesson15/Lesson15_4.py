import re
import urllib.parse
from typing import Dict, Any
from playwright.async_api import async_playwright, BrowserContext, Page

async def fetch_yahoo(context: BrowserContext, keyword: str) -> Dict[str, Any]:
    """從 Yahoo購物中心 抓取第一筆商品資訊 (DOM 解析)"""
    result = {
        "platform": "Yahoo購物中心",
        "title": "未找到相關商品",
        "price": 0,
        "url": "",
        "status": "無結果"
    }

    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://tw.buy.yahoo.com/search/product?p={encoded_kw}"
    page: Page = await context.new_page()

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(1200)
        cards = page.locator("a[href*='/gdsale/']")

        if await cards.count() > 0:
            card = cards.first
            href = await card.get_attribute("href")
            txt = await card.inner_text()
            lines = [l.strip() for l in txt.split("\n") if l.strip()]

            title = ""
            price = 0
            for l in lines:
                if l.startswith("$"):
                    digits = re.sub(r"[^\d]", "", l)
                    if digits and price == 0:
                        price = int(digits)
                elif l not in ["比較", "找相似", "活動", "券", "限時下殺", "折扣"] and not title:
                    title = l

            if title:
                result["title"] = title
                result["price"] = price
                result["url"] = href or ""
                result["status"] = "成功"
    except Exception as e:
        print(f"Yahoo 抓取失敗: {e}")
    finally:
        await page.close()

    return result

# 單獨測試 fetch_yahoo
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    res = await fetch_yahoo(context, "毛寶 貼身衣物手洗精")
    print(res)
    await browser.close()