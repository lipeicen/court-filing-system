
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 登录
    print("打开登录页面...")
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index", timeout=60000)
    time.sleep(3)
    
    # 选择律师用户
    page.get_by_text("律师用户").click()
    time.sleep(0.5)
    
    # 输入手机号
    page.locator("uni-input").filter(has_text="请输入手机号/居民身份证号").get_by_role("textbox").fill("13723715831")
    time.sleep(0.5)
    
    # 输入密码
    page.locator("input[type=\"password\"]").fill("HU1234pp")
    time.sleep(0.5)
    
    # 点击登录
    page.get_by_text("登录", exact=True).click()
    print("已点击登录")
    
    # 等待登录成功
    time.sleep(5)
    print(f"当前URL: {page.url}")
    print(f"页面标题: {page.title()}")
    
    # 截图
    page.screenshot(path="C:/court-auto-filing/debug_after_login.png")
    print("截图已保存: debug_after_login.png")
    
    # 尝试点击在线立案
    print("\n尝试点击在线立案...")
    try:
        page.get_by_text("在线立案").click()
        print("点击成功")
    except Exception as e:
        print(f"点击失败: {e}")
    
    time.sleep(3)
    page.screenshot(path="C:/court-auto-filing/debug_after_click.png")
    print("截图已保存: debug_after_click.png")
    
    # 尝试点击在线保全
    print("\n尝试点击在线保全...")
    try:
        with page.expect_popup() as popup_info:
            page.locator("uni-view").filter(has_text=re.compile(r"^保全在线保全$")).locator("uni-view").nth(3).click()
        page1 = popup_info.value
        print(f"新窗口URL: {page1.url}")
    except Exception as e:
        print(f"点击失败: {e}")
        # 尝试其他选择器
        try:
            print("尝试其他选择器...")
            page.get_by_text("保全").click()
            print("点击'保全'成功")
        except Exception as e2:
            print(f"也失败了: {e2}")
    
    time.sleep(5)
    page.screenshot(path="C:/court-auto-filing/debug_final.png")
    print("\n截图已保存: debug_final.png")
    
    browser.close()
