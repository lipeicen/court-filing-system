"""
简单调试 - 手动登录后查看表单
"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # 进入保全申请页面(假设已登录)
    print("打开保全申请页面...")
    page.goto("https://zxfw.court.gov.cn/yzwbqww/index.html")
    time.sleep(5)
    
    # 截图
    page.screenshot(path="simple_debug.png")
    print("已截图: simple_debug.png")
    
    # 获取HTML
    html = page.content()
    with open("simple_debug.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML已保存")
    
    # 查找所有单选按钮
    radios = page.locator("uni-radio").all()
    print(f"\n找到 {len(radios)} 个单选按钮:")
    for i, radio in enumerate(radios[:10]):  # 只显示前10个
        try:
            text = radio.text_content()
            print(f"  [{i}] {text.strip()}")
        except:
            pass
    
    print("\n等待10秒后关闭...")
    time.sleep(10)
    browser.close()
