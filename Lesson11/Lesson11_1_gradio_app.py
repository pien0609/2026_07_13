"""
Lesson11 - 維基百科爬蟲 Gradio 介面

使用 Playwright 自動化瀏覽器搜尋中文維基百科，擷取標題與摘要，
並透過 Gradio 建立美觀的 Web 介面。

執行方式：
    uv run Lesson11/Lesson11_1_gradio_app.py
"""

import re
import gradio as gr
from playwright.sync_api import sync_playwright, Playwright, Browser, Page


def search_wikipedia(page: Page, keyword: str) -> None:
    page.goto("https://zh.wikipedia.org")
    search_input = page.locator("#searchInput")
    search_input.fill(keyword)
    search_input.press("Enter")
    page.wait_for_selector("#firstHeading")


def get_search_result(page: Page) -> dict[str, str]:
    heading: str = page.locator("#firstHeading").inner_text()
    paragraphs = page.locator("#mw-content-text p").filter(has_text=re.compile(r"\S"))
    content: str = paragraphs.first.inner_text() if paragraphs.count() > 0 else ""
    url = page.url
    return {"heading": heading, "content": content, "url": url}


def crawl_wikipedia(keyword: str) -> tuple[str, str, str]:
    if not keyword.strip():
        return "⚠️ 請輸入關鍵字", "", ""

    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        try:
            page: Page = browser.new_page()
            search_wikipedia(page, keyword)
            result = get_search_result(page)
            return result["heading"], result["content"], result["url"]
        except Exception as e:
            return "❌ 搜尋失敗", f"錯誤訊息：{e}", ""
        finally:
            browser.close()


def build_demo() -> gr.Blocks:
    with gr.Blocks(
        title="維基百科爬蟲",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
            font=["Microsoft YaHei", "sans-serif"],
        ),
        css="""
        #header { text-align: center; padding: 1.5em 0 0.5em; }
        #header h1 { margin-bottom: 0.2em; }
        #header p { color: #666; font-size: 1.05em; }
        #search-row { margin-top: 0.8em; }
        #result-card { margin-top: 1em; }
        #footer { text-align: center; color: #aaa; font-size: 0.85em; padding-top: 1.5em; }
        """,
    ) as demo:
        gr.HTML(
            """
            <div id="header">
                <h1>📖 維基百科搜尋器</h1>
                <p>輸入關鍵字，自動搜尋中文維基百科並顯示摘要</p>
            </div>
            """
        )

        with gr.Row(elem_id="search-row"):
            keyword_input = gr.Textbox(
                label="搜尋關鍵字",
                placeholder="例如：臺灣、人工智慧、Python",
                scale=5,
                show_label=True,
            )
            search_btn = gr.Button(
                "🔍 搜尋",
                variant="primary",
                scale=1,
                min_width=120,
            )

        with gr.Group(elem_id="result-card"):
            heading_output = gr.Textbox(
                label="標題",
                interactive=False,
                max_lines=1,
            )
            content_output = gr.Textbox(
                label="摘要",
                interactive=False,
                lines=6,
            )
            url_output = gr.Textbox(
                label="網址",
                interactive=False,
                max_lines=1,
            )

        gr.HTML('<div id="footer">Lesson11 ─ 維基百科爬蟲 Gradio 介面</div>')

        search_btn.click(
            fn=crawl_wikipedia,
            inputs=keyword_input,
            outputs=[heading_output, content_output, url_output],
        )
        keyword_input.submit(
            fn=crawl_wikipedia,
            inputs=keyword_input,
            outputs=[heading_output, content_output, url_output],
        )

    return demo


if __name__ == "__main__":
    demo = build_demo()
    demo.launch()
