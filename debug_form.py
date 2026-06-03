"""
调试脚本 - 查看保全申请表单页面
"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # 先登录
    print("登录...")
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
    time.sleep(3)
    
    # 选择律师用户
    page.get_by_text("律师用户").click()
    time.sleep(1)
    
    # 输入账号密码
    inputs = page.locator("input").all()
    inputs[0].fill("13723715831")
    inputs[1].fill("HU1234pp")
    time.sleep(1)
    
    # 点击登录
    page.get_by_text("登录", exact=True).click()
    time.sleep(3)
    
    # 点击在线立案
    print("点击在线立案...")
    page.get_by_text("在线立案").click()
    time.sleep(2)
    
    # 点击在线保全
    print("点击在线保全...")
    with page.expect_popup() as page1_info:
        page.locator("uni-view").filter(has_text=re.compile(r"^保全在线保全$")).locator("uni-view").nth(3).click()
    
    page1 = page1_info.value
    time.sleep(3)
    
    # 勾选阅读须知
    print("勾选阅读须知...")
    page1.get_by_role("radio", name="我已阅读网上保全须知").click()
    time.sleep(1)
    
    # 点击创建保全申请
    print("点击创建保全申请...")
    page1.get_by_role("button", name="创建保全申请").click()
    time.sleep(3)
    
    # 截图查看表单
    page1.screenshot(path="debug_form_page.png")
    print("已截图: debug_form_page.png")
    
    # 获取表单HTML
    html = page1.content()
    with open("form_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML已保存到 form_page.html")
    
    # 查找所有单选按钮
    radios = page1.locator("uni-radio").all()
    print(f"\n找到 {len(radios)} 个单选按钮:")
    for i, radio in enumerate(radios):
        try:
            text = radio.text_content()
            print(f"  [{i}] {text.strip()}")
        except:
            pass
    
    # 查找所有输入框
    inputs = page1.locator("input").all()
    print(f"\n找到 {len(inputs)} 个输入框:")
    for i, inp in enumerate(inputs):
        try:
            placeholder = inp.get_attribute("placeholder") or ""
            input_type = inp.get_attribute("type") or "text"
            print(f"  [{i}] type={input_type}, placeholder={placeholder}")
        except:
            pass
    
    print("\n等待10秒后关闭...")
    time.sleep(10)
    browser.close()
