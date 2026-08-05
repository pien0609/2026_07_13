import asyncio
import re
import urllib.parse
from pprint import pprint
from typing import Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Locator, Page

async def fetch_momo(context: BrowserContext, keyword: str) -> Dict[str, Any]:
    """從 momo購物網 抓取第一筆商品資訊 (DOM 解析)"""
    result = {
        "platform": "momo購物網",
        "title": "未找到相關商品",
        "price": 0,
        "url": "",
        "status": "無結果"
    }

    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://www.momoshop.com.tw/search/searchShop.jsp?keyword={encoded_kw}"
    page: Page = await context.new_page()

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(1000)
        cards: Locator = page.locator("div.listArea ul li, .prdListArea ul li")
        
        if await cards.count() > 0:
            card:Locator = cards.first
            title_loc:Locator = card.locator(".prdName, h3, .goodsName")
            price_loc:Locator = card.locator(".price, .money, .prdPrice")
            link_loc:Locator = card.locator("a.goods-img-url, a.prdName, a").first

            title:str = await title_loc.first.inner_text() if await title_loc.count() > 0 else ""
            price_text:str = await price_loc.first.inner_text() if await price_loc.count() > 0 else ""
            href = await link_loc.get_attribute("href")
            href = href or ""

            digits = re.sub(r"[^\d]", "", price_text)
            price = int(digits) if digits else 0

            if href and not href.startswith("http"):
                href = f"https://www.momoshop.com.tw{href}"

            if title:
                result["title"] = title.strip()
                result["price"] = price
                result["url"] = href
                result["status"] = "成功"
    except Exception as e:
        print(f"momo 抓取失敗: {e}")
    finally:
        await page.close()

    return result

# 單獨測試 fetch_momo
async def main() -> None:
    async with async_playwright() as p:
        browser: Browser = await p.firefox.launch(headless=True)
        context: BrowserContext = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        res: Dict[str, Any] = await fetch_momo(context, "毛寶 貼身衣物手洗精")
        pprint(res)
        await browser.close()

asyncio.run(main())