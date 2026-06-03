
from playwright.sync_api import sync_playwright
import time
import ddddocr
from io import BytesIO

def solve_captcha(page):
    """解决验证码"""
    import ddddocr
    
    # 找到验证码图片
    captcha_img = None
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
            if img.count() > 0:
                # 检查是否是验证码图片
                src = img.get_attribute("src")
                if src and ("captcha" in src or "verify" in src or "code" in src):
                    captcha_img = img
                    print(f"找到验证码图片: {selector}, src={src[:50]}")
                    break
                # 尝试截图判断
                bbox = img.bounding_box()
                if bbox and bbox["width"] < 200 and bbox["height"] < 100:
                    captcha_img = img
                    print(f"找到验证码图片(按尺寸): {selector}, size={bbox['width']}x{bbox['height']}")
                    break
        except:
            continue
    
    if not captcha_img:
        print("未找到验证码图片，尝试截图所有img")
        imgs = page.locator("img").all()
        for idx, img in enumerate(imgs):
            try:
                bbox = img.bounding_box()
                if bbox:
                    print(f"  img[{idx}]: {bbox['width']}x{bbox['height']}")
            except:
                pass
        return None
    
    # 截图并识别
    try:
        screenshot = captcha_img.screenshot()
        ocr = ddddocr.DdddOcr(show_ad=False)
        result = ocr.classification(screenshot)
        print(f"验证码识别结果: {result}")
        return result
    except Exception as e:
        print(f"验证码识别失败: {e}")
        return None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    print("打开登录页面...")
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index", timeout=60000)
    time.sleep(3)
    
    print("页面标题:", page.title())
    
    # 截图看当前状态
    page.screenshot(path="C:/court-auto-filing/debug_login1.png")
    print("截图已保存: debug_login1.png")
    
    # 选择律师用户
    print("选择律师用户...")
    try:
        page.get_by_text("律师用户").click()
        print("点击成功")
    except Exception as e:
        print(f"点击失败: {e}")
    
    time.sleep(1)
    page.screenshot(path="C:/court-auto-filing/debug_login2.png")
    
    # 输入手机号
    print("输入手机号...")
    try:
        phone_input = page.locator("uni-input").filter(has_text="请输入手机号/居民身份证号").get_by_role("textbox")
        phone_input.click()
        phone_input.fill("13723715831")
        print("手机号输入成功")
    except Exception as e:
        print(f"手机号输入失败: {e}")
        # 尝试其他选择器
        try:
            inputs = page.locator("input").all()
            print(f"找到 {len(inputs)} 个input")
            for i, inp in enumerate(inputs):
                placeholder = inp.get_attribute("placeholder") or ""
                print(f"  input[{i}]: placeholder={placeholder}")
        except Exception as e2:
            print(f"获取input失败: {e2}")
    
    time.sleep(1)
    page.screenshot(path="C:/court-auto-filing/debug_login3.png")
    
    # 输入密码
    print("输入密码...")
    try:
        pwd_input = page.locator("input[type=\"password\"]")
        pwd_input.click()
        pwd_input.fill("HU1234pp")
        print("密码输入成功")
    except Exception as e:
        print(f"密码输入失败: {e}")
    
    time.sleep(1)
    page.screenshot(path="C:/court-auto-filing/debug_login4.png")
    
    # 识别验证码
    print("识别验证码...")
    captcha_text = solve_captcha(page)
    
    if captcha_text:
        try:
            captcha_input = page.locator("uni-input").filter(has_text="请输入验证码").get_by_role("textbox")
            captcha_input.click()
            captcha_input.fill(captcha_text)
            print("验证码输入成功")
        except Exception as e:
            print(f"验证码输入失败: {e}")
    
    time.sleep(1)
    page.screenshot(path="C:/court-auto-filing/debug_login5.png")
    
    # 点击登录
    print("点击登录...")
    try:
        page.get_by_text("登录", exact=True).click()
        print("点击登录成功")
    except Exception as e:
        print(f"点击登录失败: {e}")
    
    time.sleep(5)
    page.screenshot(path="C:/court-auto-filing/debug_login6.png")
    
    print("当前URL:", page.url)
    print("页面标题:", page.title())
    
    # 等待看是否登录成功
    time.sleep(10)
    page.screenshot(path="C:/court-auto-filing/debug_login7.png")
    
    browser.close()
    print("测试完成")
