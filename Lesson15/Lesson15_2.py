from playwright.async_api import async_playwright, Browser,BrowserContext,APIResponse
from typing import Dict,Any
from pprint import pprint
import urllib.parse

async def fetch_pchome(context:BrowserContext, keyword: str) -> Dict[str, Any]:
    """從 PChome 24h 購物抓取第一筆商品資訊 (API 方式)"""
    result = {
        "platform": "PChome 24h",
        "title": "未找到相關商品",
        "price": 0,
        "url": "",
        "status": "無結果"
    }
    encoded_kw= urllib.parse.quote(keyword)
    api_url = f"https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={encoded_kw}&page=1"
    try:
        response:APIResponse = await context.request.get(api_url)
        if response.status == 200:
            data:Dict = await response.json()
            prods:list = data.get("prods",[])
            if prods:
                item:dict = prods[0]
                result['title'] = item.get("name", "未知的商品標題")
                result["price"] = int(item.get("price", 0))
                result["url"] = f"https://24h.pchome.com.tw/prod/{item.get('Id', '')}"
                result["status"] = "成功"
                return result
    except Exception as e:
        print(f"PChome 抓取失敗: {e}")
    return result


async with async_playwright() as p:
    browser:Browser = await p.firefox.launch(headless=True)
    context:BrowserContext = await browser.new_context()
    res:Dict[str, Any] = await fetch_pchome(context, "毛寶 洗衣槽")
    pprint(res)
    await browser.close()
