
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://zxfw.court.gov.cn/")
    print("页面标题:", page.title())
    print("当前URL:", page.url)
    # 截图看状态
    page.screenshot(path="C:/court-auto-filing/debug_login.png")
    print("截图已保存: C:/court-auto-filing/debug_login.png")
    time.sleep(5)
    browser.close()
