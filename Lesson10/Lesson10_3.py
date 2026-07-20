
import asyncio
from playwright.sync_api import async_playwright,Browser,Page

async def main()
async with async_playwright() as p:
    #啟動瀏覽器
    browser:Browser = await p.chromium.launch()
    page:Page = await browser.new_page()
    await browser.close()
await main()