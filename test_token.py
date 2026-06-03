
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # Try to access with existing token
    with open("token.txt", "r") as f:
        token = f.read().strip()
    
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/apply-baoquan/index")
    time.sleep(2)
    
    # Set token
    page.evaluate(f"() => {{ localStorage.setItem('zxfwtoken', '{token}'); }}")
    
    # Refresh
    page.reload()
    time.sleep(3)
    
    print(f"URL: {page.url}")
    title = page.evaluate("() => document.title")
    print(f"Title: {title}")
    
    # Check if logged in
    text = page.evaluate("() => document.body.innerText")
    if "在线立案" in text or "保全" in text:
        print("Token valid!")
    else:
        print("Token expired or invalid")
        print("Page text:", text[:500])
    
    browser.close()
