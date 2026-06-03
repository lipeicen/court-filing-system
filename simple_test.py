
from playwright.sync_api import sync_playwright
import time
import ddddocr

def solve_captcha(page):
    """解决验证码"""
    try:
        selectors = [
            "img[mode='aspectFit']",
            "img.captcha",
            "img[src*='captcha']",
            "img[src*='verify']",
            "uni-image img",
            "img"
        ]
        for selector in selectors:
            try:
                img = page.locator(selector).first
                if img.is_visible():
                    screenshot = img.screenshot()
                    ocr = ddddocr.DdddOcr(show_ad=False)
                    result = ocr.classification(screenshot)
                    print(f"验证码识别: {result}")
                    return result
            except:
                continue
    except Exception as e:
        print(f"验证码识别失败: {e}")
    return None

def auto_login(page, max_retries=3):
    """自动登录"""
    print("=" * 50)
    print("开始登录")
    print("=" * 50)
    
    for attempt in range(max_retries):
        print(f"\n第 {attempt + 1} 次尝试...")
        
        page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index", timeout=60000)
        time.sleep(3)
        
        print("选择律师用户...")
        page.get_by_text("律师用户").click()
        time.sleep(0.5)
        
        print("输入手机号...")
        phone_input = page.locator("uni-input").filter(has_text="请输入手机号/居民身份证号").get_by_role("textbox")
        phone_input.click()
        phone_input.fill("13723715831")
        time.sleep(0.5)
        
        print("输入密码...")
        pwd_input = page.locator("input[type=\"password\"]")
        pwd_input.click()
        pwd_input.fill("HU1234pp")
        time.sleep(0.5)
        
        print("识别验证码...")
        captcha_text = solve_captcha(page)
        if captcha_text:
            captcha_input = page.locator("uni-input").filter(has_text="请输入验证码").get_by_role("textbox")
            captcha_input.click()
            captcha_input.fill(captcha_text)
        time.sleep(0.5)
        
        print("点击登录...")
        page.get_by_text("登录", exact=True).click()
        
        try:
            page.wait_for_selector("text=在线立案", timeout=60000)
            print("登录成功!")
            return True
        except:
            print("登录失败，准备重试...")
            time.sleep(2)
            continue
    
    print(f"\n{max_retries} 次尝试均失败")
    return False

def test_navigation(page):
    """测试导航到保全申请"""
    print("\n测试导航...")
    
    # 点击在线立案
    print("点击在线立案...")
    try:
        page.get_by_text("在线立案").click()
        print("  成功")
    except Exception as e:
        print(f"  失败: {e}")
        return None
    
    time.sleep(2)
    page.screenshot(path="C:/court-auto-filing/test_step1.png")
    
    # 点击在线保全
    print("点击在线保全...")
    try:
        with page.expect_popup() as popup_info:
            page.locator("uni-view").filter(has_text=re.compile(r"^保全在线保全$")).locator("uni-view").nth(3).click()
        page1 = popup_info.value
        print(f"  成功，新窗口: {page1.url}")
    except Exception as e:
        print(f"  失败: {e}")
        return None
    
    time.sleep(3)
    page1.screenshot(path="C:/court-auto-filing/test_step2.png")
    
    # 勾选阅读须知
    print("勾选阅读须知...")
    try:
        page1.get_by_role("radio", name="我已阅读网上保全须知").click()
        print("  成功")
    except Exception as e:
        print(f"  失败: {e}")
    
    time.sleep(1)
    
    # 点击创建保全申请
    print("点击创建保全申请...")
    try:
        page1.get_by_role("button", name="创建保全申请").click()
        print("  成功")
    except Exception as e:
        print(f"  失败: {e}")
    
    time.sleep(2)
    page1.screenshot(path="C:/court-auto-filing/test_step3.png")
    
    return page1

import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 登录
    if auto_login(page):
        print("\n登录成功，开始测试导航...")
        page1 = test_navigation(page)
        
        if page1:
            print("\n导航成功!")
            print("请检查截图文件:")
            print("  test_step1.png - 点击在线立案后")
            print("  test_step2.png - 点击在线保全后")
            print("  test_step3.png - 点击创建保全申请后")
            
            # 保持浏览器打开供检查
            print("\n浏览器保持打开30秒...")
            time.sleep(30)
        else:
            print("\n导航失败")
    else:
        print("\n登录失败")
    
    browser.close()
