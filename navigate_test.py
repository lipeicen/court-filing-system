
from playwright.sync_api import sync_playwright
import time
import ddddocr

def solve_captcha(page):
    import ddddocr
    try:
        img = page.locator("uni-image img").first
        bbox = img.bounding_box()
        if bbox and bbox["width"] < 200 and bbox["height"] < 100:
            screenshot = img.screenshot()
            ocr = ddddocr.DdddOcr(show_ad=False)
            return ocr.classification(screenshot)
    except:
        pass
    return None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 登录
    print("登录...")
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index", timeout=60000)
    time.sleep(3)
    page.get_by_text("律师用户").click()
    time.sleep(0.5)
    page.locator("uni-input").filter(has_text="请输入手机号/居民身份证号").get_by_role("textbox").fill("13723715831")
    page.locator("input[type=\"password\"]").fill("HU1234pp")
    captcha = solve_captcha(page)
    if captcha:
        page.locator("uni-input").filter(has_text="请输入验证码").get_by_role("textbox").fill(captcha)
    page.get_by_text("登录", exact=True).click()
    time.sleep(5)
    
    print("当前URL:", page.url)
    print("标题:", page.title())
    
    # 导航到保全申请
    print("\n导航到保全申请...")
    # 尝试点击在线立案
    try:
        page.get_by_text("在线立案").click()
        print("点击在线立案")
    except:
        print("未找到在线立案")
    
    time.sleep(3)
    page.screenshot(path="C:/court-auto-filing/debug_step1.png")
    
    # 尝试点击保全
    try:
        page.get_by_text("保全").click()
        print("点击保全")
    except:
        print("未找到保全按钮")
    
    time.sleep(3)
    page.screenshot(path="C:/court-auto-filing/debug_step2.png")
    
    # 尝试点击申请保全
    try:
        page.get_by_text("申请保全").click()
        print("点击申请保全")
    except:
        print("未找到申请保全")
    
    time.sleep(5)
    page.screenshot(path="C:/court-auto-filing/debug_step3.png")
    
    print("\n当前URL:", page.url)
    print("请检查截图看是否正确导航到保全申请页面")
    
    time.sleep(10)
    browser.close()
