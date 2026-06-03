"""
调试脚本 - 测试登录流程
"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # 进入登录页
    print("打开登录页面...")
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
    time.sleep(3)
    
    # 截图查看页面
    page.screenshot(path="debug_login_page.png")
    print("已截图: debug_login_page.png")
    
    # 选择律师用户
    print("选择律师用户...")
    page.get_by_text("律师用户").click()
    time.sleep(1)
    
    # 截图
    page.screenshot(path="debug_after_select.png")
    print("已截图: debug_after_select.png")
    
    # 输入手机号
    print("输入手机号...")
    try:
        phone_input = page.locator("uni-input").filter(has_text="请输入手机号/居民身份证号").get_by_role("textbox")
        phone_input.click()
        phone_input.fill("13723715831")
        print("手机号输入成功")
    except Exception as e:
        print(f"手机号输入失败: {e}")
    
    # 截图
    page.screenshot(path="debug_after_phone.png")
    print("已截图: debug_after_phone.png")
    
    # 保持浏览器打开
    print("\n等待10秒后关闭...")
    time.sleep(10)
    
    browser.close()
