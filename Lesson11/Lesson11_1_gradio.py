"""
Lesson11_1_gradio.py - 維基百科爬蟲 Gradio 介面

使用 Gradio 建立美觀的 Web 介面，讓使用者可以輸入關鍵字，
透過 Playwright 自動化搜尋中文維基百科，並顯示搜尋結果的標題與摘要。
"""

import re
import gradio as gr
from datetime import datetime
from playwright.sync_api import sync_playwright, Playwright, Browser, Page


def launch_browser(p: Playwright) -> Browser:
    """啟動 Chromium 瀏覽器實例。"""
    return p.chromium.launch()


def search_wikipedia(page: Page, keyword: str) -> None:
    """在中文維基百科搜尋指定關鍵字。"""
    page.goto("https://zh.wikipedia.org")
    search_input = page.locator("#searchInput")
    search_input.fill(keyword)
    page.screenshot(path=f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    search_input.press("Enter")
    page.wait_for_selector("#firstHeading")


def get_search_result(page: Page) -> dict[str, str]:
    """擷取搜尋結果頁面的標題與第一段摘要。"""
    heading: str = page.locator("#firstHeading").inner_text()
    paragraphs = page.locator("#mw-content-text p").filter(has_text=re.compile(r"\S"))
    content: str = paragraphs.first.inner_text() if paragraphs.count() > 0 else ""
    return {"heading": heading, "content": content[:100]}


def crawl_wikipedia(keyword: str) -> tuple[str, str]:
    """爬蟲主流程，回傳 (標題, 摘要)。"""
    with sync_playwright() as p:
        browser = launch_browser(p)
        try:
            page = browser.new_page()
            search_wikipedia(page, keyword)
            result = get_search_result(page)
            return result["heading"], result["content"]
        except Exception as e:
            return "搜尋失敗", str(e)
        finally:
            browser.close()


def search_action(keyword: str) -> tuple[str, str]:
    """Gradio 介面的搜尋動作。"""
    if not keyword.strip():
        return "請輸入搜尋關鍵字", ""
    return crawl_wikipedia(keyword.strip())


with gr.Blocks(
    title="維基百科搜尋器",
    theme=gr.themes.Soft(),
    css="""
    .container { max-width: 800px; margin: auto; }
    .header { text-align: center; margin-bottom: 20px; }
    """
) as demo:
    gr.Markdown(
        """
        <div class="header">
        <h1>維基百科搜尋器</h1>
        <p>輸入關鍵字，自動搜尋中文維基百科並顯示摘要</p>
        </div>
        """
    )

    with gr.Row():
        keyword_input = gr.Textbox(
            label="搜尋關鍵字",
            placeholder="請輸入要搜尋的關鍵字...",
            scale=4,
        )
        search_btn = gr.Button("搜尋", variant="primary", scale=1)

    with gr.Row():
        with gr.Column():
            heading_output = gr.Textbox(label="標題", interactive=False)
        with gr.Column():
            content_output = gr.Textbox(label="摘要", interactive=False, lines=3)

    search_btn.click(fn=search_action, inputs=keyword_input, outputs=[heading_output, content_output])
    keyword_input.submit(fn=search_action, inputs=keyword_input, outputs=[heading_output, content_output])

if __name__ == "__main__":
    demo.launch()
