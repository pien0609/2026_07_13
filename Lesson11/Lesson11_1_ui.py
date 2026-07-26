"""
Lesson11 - 維基百科爬蟲 Gradio 介面

使用 Playwright 自動化瀏覽器，前往中文維基百科搜尋指定關鍵字，
擷取搜尋結果的標題與摘要內容，並透過 Gradio 介面展示。

執行方式：
    uv run Lesson11/Lesson11_1_ui.py
"""

import re
import gradio as gr
from playwright.sync_api import sync_playwright, Playwright, Browser, Page


def search_wikipedia(page: Page, keyword: str) -> None:
    """在中文維基百科搜尋指定關鍵字。"""
    page.goto("https://zh.wikipedia.org")
    search_input = page.locator("#searchInput")
    search_input.fill(keyword)
    search_input.press("Enter")
    page.wait_for_selector("#firstHeading")


def get_search_result(page: Page) -> dict[str, str]:
    """擷取搜尋結果頁面的標題與第一段摘要。"""
    heading: str = page.locator("#firstHeading").inner_text()
    paragraphs = page.locator("#mw-content-text p").filter(has_text=re.compile(r"\S"))
    content: str = paragraphs.first.inner_text() if paragraphs.count() > 0 else ""
    return {"heading": heading, "content": content[:300]}


def crawl_wikipedia(keyword: str) -> tuple[str, str]:
    """Gradio 回呼函式：執行爬蟲並回傳標題與摘要。"""
    if not keyword.strip():
        return "請輸入搜尋關鍵字", ""

    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        try:
            page: Page = browser.new_page()
            search_wikipedia(page, keyword)
            result = get_search_result(page)
            return result["heading"], result["content"]
        except Exception as e:
            return "搜尋失敗", f"錯誤訊息：{e}"
        finally:
            browser.close()


with gr.Blocks(
    title="維基百科爬蟲",
    theme=gr.themes.Soft(),
    css="""
    .title { text-align: center; margin-bottom: 0.5em; }
    .footer { text-align: center; color: #999; font-size: 0.85em; margin-top: 1.5em; }
    """,
) as demo:
    gr.Markdown("# 維基百科爬蟲", elem_classes=["title"])
    gr.Markdown("輸入關鍵字，自動搜尋中文維基百科並擷取摘要內容。")

    with gr.Row():
        keyword_input = gr.Textbox(
            label="搜尋關鍵字",
            placeholder="請輸入關鍵字，例如：臺灣",
            scale=4,
        )
        search_btn = gr.Button("搜尋", variant="primary", scale=1)

    with gr.Row():
        heading_output = gr.Textbox(label="標題", interactive=False)
        content_output = gr.Textbox(label="摘要", lines=6, interactive=False)

    search_btn.click(fn=crawl_wikipedia, inputs=keyword_input, outputs=[heading_output, content_output])
    keyword_input.submit(fn=crawl_wikipedia, inputs=keyword_input, outputs=[heading_output, content_output])

    gr.Markdown("---\nLesson11 - 維基百科爬蟲 Gradio 介面", elem_classes=["footer"])

if __name__ == "__main__":
    demo.launch()
