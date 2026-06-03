from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = p.chromium.launch().new_page()
    
    # 进入保全页面
    page.goto("https://zxfw.court.gov.cn/yzwbqww/index.html#/home/login?type=yzw")
    time.sleep(3)
    
    # 勾选阅读须知
    page.get_by_role("radio", name="我已阅读网上保全须知").click()
    time.sleep(1)
    
    # 点击创建保全申请
    page.get_by_role("button", name="创建保全申请").click()
    time.sleep(2)
    
    # 截图查看申请人类型选项
    page.screenshot(path=r"C:\court-auto-filing\applicant_type.png", full_page=True)
    print("✓ 截图已保存")
    
    # 获取所有radio按钮
    radios = page.locator("input[type='radio']").all()
    print(f"找到 {len(radios)} 个radio按钮")
    
    for i, radio in enumerate(radios):
        try:
            label = radio.evaluate("el => el.nextElementSibling?.textContent || el.parentElement?.textContent")
            print(f"  [{i}] {label}")
        except:
            pass
    
    browser.close()
