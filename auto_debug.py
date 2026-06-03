from playwright.sync_api import sync_playwright
import time
import re
import ddddocr

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    print("登录...")
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
    time.sleep(3)
    
    page.get_by_text("律师用户").click()
    time.sleep(1)
    
    inputs = page.locator("input").all()
    inputs[0].fill("13723715831")
    inputs[1].fill("HU1234pp")
    time.sleep(1)
    
    print("识别验证码...")
    try:
        captcha_img = page.locator("uni-image img").first
        captcha_img.screenshot(path="debug_captcha.png")
        ocr = ddddocr.DdddOcr(show_ad=False)
        with open("debug_captcha.png", "rb") as f:
            img_bytes = f.read()
        captcha = ocr.classification(img_bytes)
        print(f"验证码: {captcha}")
        if captcha and len(captcha) == 4:
            inputs[2].fill(captcha)
    except Exception as e:
        print(f"失败: {e}")
    
    page.get_by_text("登录", exact=True).click()
    time.sleep(5)
    
    if "在线立案" in page.content():
        print("登录成功!")
    else:
        print("登录失败")
        page.screenshot(path="login_failed_debug.png")
        browser.close()
        exit()
    
    print("点击在线立案...")
    page.get_by_text("在线立案").click()
    time.sleep(2)
    
    print("点击在线保全...")
    with page.expect_popup() as page1_info:
        page.locator("uni-view").filter(has_text=re.compile(r"^保全在线保全$")).locator("uni-view").nth(3).click()
    
    page1 = page1_info.value
    print(f"新窗口: {page1.url}")
    time.sleep(5)
    
    print("勾选阅读须知...")
    try:
        page1.get_by_role("radio", name="我已阅读网上保全须知").click()
    except:
        page1.evaluate('() => { const radio = document.querySelector("uni-radio"); if (radio) radio.click(); }')
    time.sleep(1)
    
    print("点击创建保全申请...")
    try:
        page1.get_by_role("button", name="创建保全申请").click()
    except:
        page1.evaluate('() => { const btn = Array.from(document.querySelectorAll("uni-button")).find(b => b.textContent.includes("创建保全申请")); if (btn) btn.click(); }')
    time.sleep(5)
    
    page1.screenshot(path="form_debug.png")
    print("已截图: form_debug.png")
    
    html = page1.content()
    with open("form_debug.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML已保存")
    
    print("\n分析表单...")
    texts = re.findall(r'>([^<]{2,30})<', html)
    unique_texts = set(t.strip() for t in texts if t.strip())
    print(f"页面文本 ({len(unique_texts)} 个):")
    for t in sorted(unique_texts)[:30]:
        print(f"  - {t}")
    
    radios = page1.locator("uni-radio").all()
    print(f"\n单选按钮 ({len(radios)} 个):")
    for i, radio in enumerate(radios):
        try:
            text = radio.text_content()
            print(f"  [{i}] {text.strip()}")
        except:
            pass
    
    inputs = page1.locator("input").all()
    print(f"\n输入框 ({len(inputs)} 个):")
    for i, inp in enumerate(inputs):
        try:
            placeholder = inp.get_attribute("placeholder") or ""
            print(f"  [{i}] {placeholder}")
        except:
            pass
    
    print("\n等待20秒...")
    time.sleep(20)
    browser.close()
